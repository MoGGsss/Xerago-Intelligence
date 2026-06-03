"""Pydantic response models for intelligence API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DepartmentMappingItem(BaseModel):
    department_name: str
    department_relevance_score: int = Field(ge=0, le=100)
    impact_summary: str | None = None
    impact_category: str | None = None
    opportunity_type: str | None = None
    department_opportunity_score: int | None = Field(default=None, ge=0, le=100)
    impact_reason: str | None = None
    impact_version: str | None = None


class DepartmentRegistryItem(BaseModel):
    slug: str
    display_name: str


class IntelligenceItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    strategic_score: int | None = None
    priority_level: str | None = None
    departments: list[DepartmentMappingItem] = Field(default_factory=list)
    department: str | None = None


class IntelligenceListResponse(BaseModel):
    items: list[IntelligenceItem]
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total: int = Field(ge=0)


class HealthResponse(BaseModel):
    status: str
    database: str
