"""Department Impact Engine input and output types."""

from __future__ import annotations

from dataclasses import dataclass

from xerago_intelligence.taxonomy.impact_rules import DEPARTMENT_IMPACT_VERSION


@dataclass(frozen=True)
class DepartmentImpactInput:
    """Enrichment text plus one mapped department row."""

    title: str
    summary: str
    why_it_matters: str
    domain: str
    signal_type: str
    department_name: str
    department_relevance_score: int


@dataclass(frozen=True)
class DepartmentImpactResult:
    """Rule-generated impact fields for one department mapping row."""

    impact_summary: str
    impact_category: str
    opportunity_type: str
    department_opportunity_score: int
    impact_reason: str
    impact_version: str = DEPARTMENT_IMPACT_VERSION
