"""Pydantic models for RSS source registry API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class RssSourceItem(BaseModel):
    source_id: str
    source_name: str
    source_url: str
    rss_url: str
    source_tier: int = Field(ge=1, le=3)
    active_flag: bool
    failure_count: int
    last_health_status: str | None
    last_success_at: datetime | None
    last_failure_at: datetime | None
    last_run_at: datetime | None


class RssSourceRunItem(BaseModel):
    run_id: str
    source_id: str
    started_at: datetime
    finished_at: datetime
    status: str
    http_status: int | None
    entries_fetched: int
    entries_inserted: int
    entries_skipped_dup: int
    entries_skipped_cursor: int
    error_message: str | None = None


class SourceStatsItem(BaseModel):
    source_id: str
    source_name: str
    source_tier: int
    active_flag: bool
    last_health_status: str | None
    total_artifacts: int
    artifacts_last_24h: int
    estimated_daily_articles: float


class SourceStatsResponse(BaseModel):
    sources: list[SourceStatsItem]
    active_source_count: int
    total_artifacts: int
    artifacts_last_24h: int
    estimated_daily_articles_total: float
    duplicate_protection: str = (
        "Global URL deduplication via normalized url unique index on artifacts"
    )


class SourceHealthResponse(BaseModel):
    sources: list[RssSourceItem]
    recent_runs: list[RssSourceRunItem]
