"""Canonical impact category registry for the Department Impact Engine."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ImpactCategory:
    slug: str
    display_name: str


IMPACT_CATEGORIES: tuple[ImpactCategory, ...] = (
    ImpactCategory("ai-coding", "AI Coding"),
    ImpactCategory("agentic-ai", "Agentic AI"),
    ImpactCategory("campaign-automation", "Campaign Automation"),
    ImpactCategory("content-generation", "Content Generation"),
    ImpactCategory("personalization", "Personalization"),
    ImpactCategory("forecasting", "Forecasting"),
    ImpactCategory("analytics", "Analytics"),
    ImpactCategory("lead-scoring", "Lead Scoring"),
    ImpactCategory("customer-support", "Customer Support"),
    ImpactCategory("workflow-automation", "Workflow Automation"),
    ImpactCategory("knowledge-management", "Knowledge Management"),
    ImpactCategory("governance", "Governance"),
    ImpactCategory("security", "Security"),
)

IMPACT_CATEGORY_BY_SLUG: dict[str, ImpactCategory] = {
    item.slug: item for item in IMPACT_CATEGORIES
}
IMPACT_CATEGORY_BY_NAME: dict[str, ImpactCategory] = {
    item.display_name: item for item in IMPACT_CATEGORIES
}
IMPACT_CATEGORY_NAMES: frozenset[str] = frozenset(IMPACT_CATEGORY_BY_NAME)


def is_valid_impact_category(name: str) -> bool:
    return name.strip() in IMPACT_CATEGORY_BY_NAME
