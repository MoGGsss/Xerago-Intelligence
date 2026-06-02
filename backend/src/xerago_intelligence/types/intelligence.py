"""Read-model types for intelligence API responses."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class IntelligenceRecord:
    artifact_id: str
    title: str
    url: str
    published_at: datetime
    summary: str
    why_it_matters: str
    domain: str
    signal_type: str
    confidence_score: int
    validation_status: str
    strategic_score: int | None
    priority_level: str | None
    department: str | None


@dataclass(frozen=True)
class IntelligencePage:
    items: list[IntelligenceRecord]
    page: int
    page_size: int
    total: int
