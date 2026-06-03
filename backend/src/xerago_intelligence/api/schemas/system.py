"""Pydantic models for system status API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class IntelligenceRunSummary(BaseModel):
    run_id: str
    started_at: datetime
    completed_at: datetime | None = None
    sources_polled: int = 0
    articles_found: int = 0
    articles_inserted: int = 0
    articles_filtered: int = 0
    articles_enriched: int = 0
    articles_scored: int = 0
    status: str


class SystemStatusResponse(BaseModel):
    status: str = Field(description="healthy | degraded | unhealthy")
    last_run: datetime | None = None
    next_run: datetime | None = None
    active_sources: int = 0
    articles_today: int = 0
    last_run_summary: IntelligenceRunSummary | None = None
