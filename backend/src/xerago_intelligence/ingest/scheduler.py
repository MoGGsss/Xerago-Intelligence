"""Background scheduler for automated intelligence refresh (Phase 9)."""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass

from xerago_intelligence.db import session_scope
from xerago_intelligence.db.repositories.rss_source_repository import RssSourceRepository
from xerago_intelligence.ingest import scheduler_state
from xerago_intelligence.ingest.intelligence_refresh import IntelligenceRefreshService

logger = logging.getLogger(__name__)

DEFAULT_INTERVAL_SECONDS = 15 * 60


@dataclass(frozen=True)
class ScheduledSource:
    source_id: str
    feed_url: str


class IngestionScheduler:
    """Polls active RSS sources every 15 minutes and runs the intelligence pipeline."""

    def __init__(self, *, interval_seconds: int = DEFAULT_INTERVAL_SECONDS) -> None:
        self._interval_seconds = max(1, int(interval_seconds))
        self._stop_event = threading.Event()
        self._wake_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._run_lock = threading.Lock()

    @property
    def interval_seconds(self) -> int:
        return self._interval_seconds

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        scheduler_state.register_scheduler(self)
        self._thread = threading.Thread(
            target=self._run_loop,
            name="intelligence-refresh-scheduler",
            daemon=True,
        )
        self._thread.start()
        logger.info(
            "Intelligence refresh scheduler started (interval=%ss)",
            self._interval_seconds,
        )

    def stop(self, *, timeout_seconds: float = 5.0) -> None:
        self._stop_event.set()
        self._wake_event.set()
        if self._thread is not None:
            self._thread.join(timeout=timeout_seconds)
        logger.info("Intelligence refresh scheduler stopped")

    def trigger_now(self) -> None:
        """Request an immediate refresh cycle."""
        self._wake_event.set()

    def _run_loop(self) -> None:
        logger.info(
            "Scheduler loop active (thread=%s interval=%ss)",
            threading.current_thread().name,
            self._interval_seconds,
        )
        self._run_once()
        while not self._stop_event.is_set():
            logger.info(
                "Scheduler tick: waiting up to %ss for next cycle",
                self._interval_seconds,
            )
            self._wake_event.wait(timeout=self._interval_seconds)
            self._wake_event.clear()
            if self._stop_event.is_set():
                break
            self._run_once()

    def _run_once(self) -> None:
        if not self._run_lock.acquire(blocking=False):
            logger.warning("Skipping refresh cycle; previous cycle still running")
            return
        scheduler_state.mark_cycle_started()
        logger.info("Scheduler cycle start")
        try:
            with session_scope() as session:
                repo = RssSourceRepository(session)
                if repo.count_all() == 0:
                    logger.info("RSS registry empty — seeding Phase 8 catalog")
                    repo.seed_phase8_catalog()
                    session.commit()

                service = IntelligenceRefreshService(session)
                cycle = service.run_cycle()
                if cycle.fatal_error:
                    logger.error(
                        "Scheduler cycle recorded failure in intelligence_runs: %s",
                        cycle.fatal_error,
                    )
                else:
                    logger.info(
                        "Scheduler cycle committed run status=%s sources_polled=%s "
                        "articles_ingested=%s articles_enriched=%s",
                        cycle.status,
                        cycle.metrics.sources_polled,
                        cycle.metrics.articles_inserted,
                        cycle.metrics.articles_enriched,
                    )
        except Exception:
            logger.exception("Scheduler cycle aborted before intelligence_runs commit")
        finally:
            scheduler_state.mark_cycle_completed()
            logger.info("Scheduler cycle end")
            self._run_lock.release()
