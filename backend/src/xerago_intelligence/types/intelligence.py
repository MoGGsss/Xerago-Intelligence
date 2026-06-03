"""Read-model types for intelligence API responses."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DepartmentMappingItem:
    department_name: str
    department_relevance_score: int
    impact_summary: str | None = None
    impact_category: str | None = None
    opportunity_type: str | None = None
    department_opportunity_score: int | None = None
    impact_reason: str | None = None
    impact_version: str | None = None


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
    departments: tuple[DepartmentMappingItem, ...]
    department: str | None


@dataclass(frozen=True)
class IntelligencePage:
    items: list[IntelligenceRecord]
    page: int
    page_size: int
    total: int
