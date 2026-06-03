"""Orchestrates one intelligence refresh cycle across all active RSS sources."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from xerago_intelligence.db.repositories.artifact_repository import ArtifactRepository
from xerago_intelligence.db.repositories.department_mapping_repository import (
    DepartmentMappingRepository,
)
from xerago_intelligence.db.repositories.intelligence_run_repository import (
    IntelligenceRunMetrics,
    IntelligenceRunRepository,
)
from xerago_intelligence.db.repositories.rss_source_repository import RssSourceRepository
from xerago_intelligence.enrichment.service import ArtifactEnrichmentService
from xerago_intelligence.filtering import EnrichmentSkippedError
from xerago_intelligence.ingest.source_health import SourceHealthMonitor

logger = logging.getLogger(__name__)


@dataclass
class SourceCycleResult:
    source_id: str
    fetched: int = 0
    inserted: int = 0
    filtered: int = 0
    enriched: int = 0
    scored: int = 0
    mapped: int = 0
    impacted: int = 0
    failed: bool = False


@dataclass
class IntelligenceRefreshCycle:
    """Aggregated metrics for a full scheduler cycle."""

    metrics: IntelligenceRunMetrics = field(default_factory=IntelligenceRunMetrics)
    source_failures: int = 0
    fatal_error: str | None = None
    articles_mapped: int = 0
    articles_impacted: int = 0

    def add_source(self, result: SourceCycleResult) -> None:
        self.metrics.sources_polled += 1
        self.metrics.articles_found += result.fetched
        self.metrics.articles_inserted += result.inserted
        self.metrics.articles_filtered += result.filtered
        self.metrics.articles_enriched += result.enriched
        self.metrics.articles_scored += result.scored
        self.articles_mapped += result.mapped
        self.articles_impacted += result.impacted
        if result.failed:
            self.source_failures += 1

    @property
    def status(self) -> str:
        if self.fatal_error:
            return "failure"
        if self.source_failures > 0:
            return "partial"
        return "success"


class IntelligenceRefreshService:
    """RSS ingest → dedupe → negative filter → enrich → score → department map."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._sources = RssSourceRepository(session)
        self._artifacts = ArtifactRepository(session)
        self._runs = IntelligenceRunRepository(session)

    def run_cycle(self) -> IntelligenceRefreshCycle:
        cycle = IntelligenceRefreshCycle()
        run = self._runs.start_run()
        run_id = run.run_id
        logger.info("Intelligence refresh cycle start run_id=%s status=running", run_id)
        try:
            active_sources = self._sources.list_active()
            if not active_sources:
                logger.info("Intelligence refresh: no active RSS sources")
                self._runs.complete_run(
                    run_id,
                    metrics=cycle.metrics,
                    status="success",
                )
                self._session.flush()
                logger.info(
                    "Intelligence refresh cycle completed run_id=%s status=success "
                    "sources_polled=0",
                    run_id,
                )
                return cycle

            logger.info(
                "Intelligence refresh polling sources=%s",
                len(active_sources),
            )
            for source in active_sources:
                result = self._process_source(
                    source_id=source.source_id,
                    feed_url=source.rss_url,
                )
                cycle.add_source(result)
                logger.info(
                    "Intelligence refresh source=%s fetched=%s inserted=%s "
                    "enriched=%s mapped=%s impacted=%s failed=%s",
                    source.source_id,
                    result.fetched,
                    result.inserted,
                    result.enriched,
                    result.mapped,
                    result.impacted,
                    result.failed,
                )

            self._runs.complete_run(
                run_id,
                metrics=cycle.metrics,
                status=cycle.status,
            )
            self._session.flush()
            logger.info(
                "Intelligence refresh cycle completed run_id=%s status=%s "
                "sources_polled=%s articles_ingested=%s articles_enriched=%s "
                "articles_mapped=%s articles_impacted=%s articles_filtered=%s",
                run_id,
                cycle.status,
                cycle.metrics.sources_polled,
                cycle.metrics.articles_inserted,
                cycle.metrics.articles_enriched,
                cycle.articles_mapped,
                cycle.articles_impacted,
                cycle.metrics.articles_filtered,
            )
        except Exception as exc:
            cycle.fatal_error = str(exc)
            logger.exception(
                "Intelligence refresh cycle failed run_id=%s",
                run_id,
            )
            self._runs.complete_run(
                run_id,
                metrics=cycle.metrics,
                status="failure",
                error_message=str(exc),
            )
            self._session.flush()
        return cycle

    def _process_source(self, *, source_id: str, feed_url: str) -> SourceCycleResult:
        outcome = SourceCycleResult(source_id=source_id)
        cycle_started_at = datetime.now(timezone.utc).replace(tzinfo=None)
        try:
            monitor = SourceHealthMonitor(self._session)
            ingest_outcome = monitor.ingest_source(source_id, feed_url)
            if ingest_outcome.status != "success" or ingest_outcome.result is None:
                outcome.failed = True
                return outcome

            result = ingest_outcome.result
            outcome.fetched = result.fetched
            outcome.inserted = result.inserted

            if result.inserted == 0:
                return outcome

            artifacts = self._artifacts.list_ingested_since(
                source_id=source_id,
                ingested_since=cycle_started_at,
            )
            enrich_service = ArtifactEnrichmentService(self._session)
            mapping_repo = DepartmentMappingRepository(self._session)
            for artifact in artifacts:
                try:
                    enrich_result = enrich_service.enrich_artifact(
                        artifact.artifact_id,
                        force=False,
                    )
                    outcome.enriched += 1
                    if enrich_result.row.strategic_score is not None:
                        outcome.scored += 1
                    mappings = mapping_repo.get_by_artifact_id(artifact.artifact_id)
                    if mappings:
                        outcome.mapped += 1
                        if any(row.impact_summary for row in mappings):
                            outcome.impacted += 1
                except EnrichmentSkippedError:
                    outcome.filtered += 1
                    logger.info(
                        "Negative filter skipped artifact_id=%s source_id=%s",
                        artifact.artifact_id,
                        source_id,
                    )

            return outcome
        except Exception:
            logger.exception("Source %s failed during intelligence refresh", source_id)
            outcome.failed = True
            return outcome
