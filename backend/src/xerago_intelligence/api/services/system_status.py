"""Build system status payload for monitoring API."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from xerago_intelligence.api.schemas.system import (
    IntelligenceRunSummary,
    SystemStatusResponse,
)
from xerago_intelligence.db.connection import probe_connection
from xerago_intelligence.db.models.intelligence_run import IntelligenceRun
from xerago_intelligence.db.repositories.artifact_repository import ArtifactRepository
from xerago_intelligence.db.repositories.intelligence_run_repository import (
    IntelligenceRunRepository,
)
from xerago_intelligence.db.repositories.rss_source_repository import RssSourceRepository
from xerago_intelligence.ingest import scheduler_state


def _to_summary(run: IntelligenceRun) -> IntelligenceRunSummary:
    return IntelligenceRunSummary(
        run_id=run.run_id,
        started_at=run.started_at,
        completed_at=run.completed_at,
        sources_polled=run.sources_polled,
        articles_found=run.articles_found,
        articles_inserted=run.articles_inserted,
        articles_filtered=run.articles_filtered,
        articles_enriched=run.articles_enriched,
        articles_scored=run.articles_scored,
        status=run.status,
    )


def _derive_health_status(last_run: IntelligenceRun | None) -> str:
    if last_run is None:
        return "degraded"
    if last_run.status == "failure":
        return "unhealthy"
    if last_run.status == "partial":
        return "degraded"
    if last_run.completed_at is None:
        return "degraded"
    stale_after = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=1)
    if last_run.completed_at < stale_after:
        return "degraded"
    if not probe_connection().ok:
        return "unhealthy"
    return "healthy"


def build_system_status(session: Session) -> SystemStatusResponse:
    runs_repo = IntelligenceRunRepository(session)
    sources_repo = RssSourceRepository(session)
    artifacts_repo = ArtifactRepository(session)

    last_run = runs_repo.get_latest_completed() or runs_repo.get_latest()
    last_completed = (
        last_run.completed_at
        if last_run is not None and last_run.completed_at is not None
        else (last_run.started_at if last_run is not None else None)
    )

    next_run = scheduler_state.get_next_run_at()
    scheduler = scheduler_state.get_scheduler()
    interval = scheduler.interval_seconds if scheduler else 15 * 60
    if last_completed is not None and (
        next_run is None or next_run <= last_completed
    ):
        next_run = last_completed + timedelta(seconds=interval)

    return SystemStatusResponse(
        status=_derive_health_status(last_run),
        last_run=last_completed,
        next_run=next_run,
        active_sources=len(sources_repo.list_active()),
        articles_today=artifacts_repo.count_ingested_today(),
        last_run_summary=_to_summary(last_run) if last_run is not None else None,
    )
