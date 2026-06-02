"""Background scheduler for periodic RSS ingest + enrichment."""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from time import sleep

from xerago_intelligence.db import session_scope
from xerago_intelligence.db.repositories.artifact_repository import ArtifactRepository
from xerago_intelligence.enrichment.service import ArtifactEnrichmentService
from xerago_intelligence.ingest.rss import RssIngestionService
from xerago_intelligence.registry.loader import load_sources_registry
from xerago_intelligence.registry.models import SourceEntry

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ScheduledSource:
    source_id: str
    feed_url: str


class IngestionScheduler:
    """Runs ingestion and enrichment pipeline every fixed interval."""

    def __init__(self, *, interval_seconds: int = 15 * 60) -> None:
        self._interval_seconds = max(1, int(interval_seconds))
        self._stop_event = threading.Event()
        self._wake_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._run_lock = threading.Lock()

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._thread = threading.Thread(
            target=self._run_loop,
            name="ingestion-scheduler",
            daemon=True,
        )
        self._thread.start()
        logger.info(
            "Ingestion scheduler started (interval=%ss)",
            self._interval_seconds,
        )

    def stop(self, *, timeout_seconds: float = 5.0) -> None:
        self._stop_event.set()
        self._wake_event.set()
        if self._thread is not None:
            self._thread.join(timeout=timeout_seconds)
        logger.info("Ingestion scheduler stopped")

    def trigger_now(self) -> None:
        self._wake_event.set()

    def _run_loop(self) -> None:
        # Run one cycle immediately on startup.
        self._run_once()

        while not self._stop_event.is_set():
            self._wake_event.wait(timeout=self._interval_seconds)
            self._wake_event.clear()
            if self._stop_event.is_set():
                break
            self._run_once()

    def _run_once(self) -> None:
        if not self._run_lock.acquire(blocking=False):
            logger.warning("Skipping scheduler cycle; previous cycle still running")
            return
        try:
            sources = _load_rss_sources()
            if not sources:
                logger.info("Scheduler cycle: no enabled RSS sources found")
                return
            logger.info("Scheduler cycle started for %s RSS sources", len(sources))
            for source in sources:
                self._run_source(source)
            logger.info("Scheduler cycle completed")
        except Exception:
            logger.exception("Scheduler cycle failed")
        finally:
            self._run_lock.release()

    def _run_source(self, source: ScheduledSource) -> None:
        cycle_started_at = datetime.now(timezone.utc).replace(tzinfo=None)
        try:
            with session_scope() as session:
                ingestion = RssIngestionService(session)
                try:
                    result = ingestion.ingest_feed(source.feed_url, source.source_id)
                finally:
                    ingestion.close()

                if result.inserted == 0:
                    logger.info(
                        "Source %s: no new artifacts (fetched=%s skipped=%s)",
                        source.source_id,
                        result.fetched,
                        result.skipped,
                    )
                    return

                artifacts = ArtifactRepository(session).list_ingested_since(
                    source_id=source.source_id,
                    ingested_since=cycle_started_at,
                )
                enrich_service = ArtifactEnrichmentService(session)
                enriched_count = 0
                for artifact in artifacts:
                    # Score persistence happens inside enrich_artifact().
                    enrich_service.enrich_artifact(artifact.artifact_id, force=False)
                    enriched_count += 1

                logger.info(
                    "Source %s: inserted=%s enriched=%s",
                    source.source_id,
                    result.inserted,
                    enriched_count,
                )
        except Exception:
            logger.exception("Source %s failed during scheduled processing", source.source_id)


def _load_rss_sources() -> list[ScheduledSource]:
    registry = load_sources_registry()
    selected: list[ScheduledSource] = []
    for source in registry.sources:
        if _is_enabled_rss_source(source):
            assert source.feed_url is not None
            selected.append(
                ScheduledSource(
                    source_id=source.source_id,
                    feed_url=source.feed_url,
                )
            )
    return selected


def _is_enabled_rss_source(source: SourceEntry) -> bool:
    return (
        source.enabled
        and source.ingestion_method == "pull_rss"
        and bool(source.feed_url)
    )
