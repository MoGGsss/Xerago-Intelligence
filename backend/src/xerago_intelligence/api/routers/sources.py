"""RSS source registry and statistics API."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from xerago_intelligence.api.dependencies import get_db
from xerago_intelligence.api.schemas.sources import (
    RssSourceItem,
    RssSourceRunItem,
    SourceHealthResponse,
    SourceStatsItem,
    SourceStatsResponse,
)
from xerago_intelligence.db.repositories.artifact_repository import ArtifactRepository
from xerago_intelligence.db.repositories.rss_source_repository import RssSourceRepository
from xerago_intelligence.ingest.source_catalog import PHASE_8_RSS_SOURCES

router = APIRouter(prefix="/sources", tags=["sources"])

# Planning estimates when no ingest history exists (articles/day).
_TIER_DAILY_ESTIMATES: dict[int, float] = {1: 2.5, 2: 8.0, 3: 1.2}
_CATALOG_DAILY_ESTIMATE = sum(
    _TIER_DAILY_ESTIMATES.get(seed.source_tier, 1.0) for seed in PHASE_8_RSS_SOURCES
)


def _estimate_daily(artifacts_last_24h: int, source_tier: int) -> float:
    if artifacts_last_24h > 0:
        return float(artifacts_last_24h)
    return _TIER_DAILY_ESTIMATES.get(source_tier, 1.0)


@router.get("", response_model=list[RssSourceItem])
def list_sources(db: Session = Depends(get_db)) -> list[RssSourceItem]:
    repo = RssSourceRepository(db)
    return [_to_source_item(row) for row in repo.list_all()]


@router.get("/health", response_model=SourceHealthResponse)
def source_health(
    runs_limit: int = Query(30, ge=1, le=200),
    db: Session = Depends(get_db),
) -> SourceHealthResponse:
    repo = RssSourceRepository(db)
    return SourceHealthResponse(
        sources=[_to_source_item(row) for row in repo.list_all()],
        recent_runs=[
            RssSourceRunItem(
                run_id=run.run_id,
                source_id=run.source_id,
                started_at=run.started_at,
                finished_at=run.finished_at,
                status=run.status,
                http_status=run.http_status,
                entries_fetched=run.entries_fetched,
                entries_inserted=run.entries_inserted,
                entries_skipped_dup=run.entries_skipped_dup,
                entries_skipped_cursor=run.entries_skipped_cursor,
                error_message=run.error_message,
            )
            for run in repo.list_recent_runs(limit=runs_limit)
        ],
    )


@router.get("/stats", response_model=SourceStatsResponse)
def source_stats(db: Session = Depends(get_db)) -> SourceStatsResponse:
    repo = RssSourceRepository(db)
    artifact_repo = ArtifactRepository(db)
    totals_by_source = repo.artifact_counts_by_source()
    last_24h_by_source = repo.inserted_last_24h_by_source()

    items: list[SourceStatsItem] = []
    estimated_total = 0.0
    artifacts_last_24h = 0

    for source in repo.list_all():
        last_24h = last_24h_by_source.get(source.source_id, 0)
        daily_est = _estimate_daily(last_24h, source.source_tier)
        estimated_total += daily_est
        artifacts_last_24h += last_24h
        items.append(
            SourceStatsItem(
                source_id=source.source_id,
                source_name=source.source_name,
                source_tier=source.source_tier,
                active_flag=source.active_flag,
                last_health_status=source.last_health_status,
                total_artifacts=totals_by_source.get(source.source_id, 0),
                artifacts_last_24h=last_24h,
                estimated_daily_articles=daily_est,
            )
        )

    if artifacts_last_24h == 0 and not items:
        estimated_total = _CATALOG_DAILY_ESTIMATE

    return SourceStatsResponse(
        sources=items,
        active_source_count=sum(1 for s in items if s.active_flag),
        total_artifacts=artifact_repo.count_all(),
        artifacts_last_24h=artifacts_last_24h,
        estimated_daily_articles_total=round(estimated_total, 1),
    )


def _to_source_item(row: object) -> RssSourceItem:
    from xerago_intelligence.db.models.rss_source import RssSource

    assert isinstance(row, RssSource)
    return RssSourceItem(
        source_id=row.source_id,
        source_name=row.source_name,
        source_url=row.source_url,
        rss_url=row.rss_url,
        source_tier=row.source_tier,
        active_flag=row.active_flag,
        failure_count=row.failure_count,
        last_health_status=row.last_health_status,
        last_success_at=row.last_success_at,
        last_failure_at=row.last_failure_at,
        last_run_at=row.last_run_at,
    )
