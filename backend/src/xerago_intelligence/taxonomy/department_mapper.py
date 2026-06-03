"""Compute department relevance scores from enrichment output."""

from __future__ import annotations

from dataclasses import dataclass

from xerago_intelligence.taxonomy.department_rules import (
    DEPARTMENT_MAPPING_VERSION,
    DOMAIN_DEPARTMENT_WEIGHTS,
    FALLBACK_DEPARTMENT_SLUG,
    INDUSTRY_TRENDS_FALLBACK_SLUG,
    KEYWORD_DEPARTMENT_BOOSTS,
    MAX_DEPARTMENTS_PER_ARTIFACT,
    MIN_RELEVANCE_SCORE,
    SIGNAL_DEPARTMENT_BOOSTS,
)
from xerago_intelligence.taxonomy.departments import DEPARTMENT_BY_SLUG


@dataclass(frozen=True)
class DepartmentMappingInput:
    domain: str
    signal_type: str
    summary: str
    why_it_matters: str
    confidence_score: int
    title: str = ""
    source_id: str = ""


@dataclass(frozen=True)
class DepartmentScore:
    department_name: str
    department_relevance_score: int


@dataclass(frozen=True)
class DepartmentMappingRecord:
    """Relevance plus optional Department Impact Engine fields for persistence."""

    department_name: str
    department_relevance_score: int
    impact_summary: str | None = None
    impact_category: str | None = None
    opportunity_type: str | None = None
    department_opportunity_score: int | None = None
    impact_reason: str | None = None
    impact_version: str | None = None

    @classmethod
    def from_score(cls, score: DepartmentScore) -> DepartmentMappingRecord:
        return cls(
            department_name=score.department_name,
            department_relevance_score=score.department_relevance_score,
        )


@dataclass(frozen=True)
class DepartmentMappingResult:
    departments: tuple[DepartmentScore, ...]
    mapping_version: str = DEPARTMENT_MAPPING_VERSION


class DepartmentMapper:
    """Rule-based mapper from enrichment fields to department relevance scores."""

    def compute(self, inputs: DepartmentMappingInput) -> DepartmentMappingResult:
        domain = inputs.domain.strip().lower()
        signal = _normalize_signal(inputs.signal_type)
        confidence_factor = max(0.0, min(1.0, inputs.confidence_score / 100.0))

        scores: dict[str, float] = {}

        for dept_slug, base in DOMAIN_DEPARTMENT_WEIGHTS.get(domain, {}).items():
            scores[dept_slug] = scores.get(dept_slug, 0.0) + base

        for dept_slug, boost in SIGNAL_DEPARTMENT_BOOSTS.get(signal, {}).items():
            scores[dept_slug] = scores.get(dept_slug, 0.0) + boost

        text_blob = " ".join(
            [inputs.title, inputs.summary, inputs.why_it_matters]
        ).lower()
        for keywords, dept_slug, boost in KEYWORD_DEPARTMENT_BOOSTS:
            if any(keyword in text_blob for keyword in keywords):
                scores[dept_slug] = scores.get(dept_slug, 0.0) + boost

        adjusted: list[DepartmentScore] = []
        for dept_slug, raw in scores.items():
            dept = DEPARTMENT_BY_SLUG.get(dept_slug)
            if dept is None:
                continue
            final = int(round(max(0, min(100, raw * confidence_factor))))
            if final >= MIN_RELEVANCE_SCORE:
                adjusted.append(
                    DepartmentScore(
                        department_name=dept.display_name,
                        department_relevance_score=final,
                    )
                )

        adjusted.sort(key=lambda item: item.department_relevance_score, reverse=True)
        adjusted = adjusted[:MAX_DEPARTMENTS_PER_ARTIFACT]

        if not adjusted:
            fallback_slug = (
                INDUSTRY_TRENDS_FALLBACK_SLUG
                if domain == "industry-trends"
                else FALLBACK_DEPARTMENT_SLUG
            )
            fallback = DEPARTMENT_BY_SLUG[fallback_slug]
            adjusted = [
                DepartmentScore(
                    department_name=fallback.display_name,
                    department_relevance_score=max(
                        MIN_RELEVANCE_SCORE - 5,
                        int(round(35 * confidence_factor)),
                    ),
                )
            ]

        return DepartmentMappingResult(departments=tuple(adjusted))


def _normalize_signal(signal_type: str) -> str:
    normalized = signal_type.strip().lower()
    if "/" in normalized:
        return normalized.split("/", 1)[0]
    return normalized


def primary_department(result: DepartmentMappingResult) -> str | None:
    if not result.departments:
        return None
    return result.departments[0].department_name


def department_for_domain(domain: str | None) -> str | None:
    """Deprecated shim: derive primary department from domain-only input."""
    if not domain:
        return None
    result = DepartmentMapper().compute(
        DepartmentMappingInput(
            domain=domain.strip().lower(),
            signal_type="",
            summary="",
            why_it_matters="",
            confidence_score=100,
        )
    )
    return primary_department(result)
