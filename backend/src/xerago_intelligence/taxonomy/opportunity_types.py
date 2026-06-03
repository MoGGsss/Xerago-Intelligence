"""Canonical opportunity type registry for the Department Impact Engine."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OpportunityType:
    slug: str
    display_name: str


OPPORTUNITY_TYPES: tuple[OpportunityType, ...] = (
    OpportunityType("revenue-growth", "Revenue Growth"),
    OpportunityType("productivity", "Productivity"),
    OpportunityType("cost-reduction", "Cost Reduction"),
    OpportunityType("automation", "Automation"),
    OpportunityType("compliance", "Compliance"),
    OpportunityType("risk-management", "Risk Management"),
    OpportunityType("innovation", "Innovation"),
    OpportunityType("customer-experience", "Customer Experience"),
    OpportunityType("employee-experience", "Employee Experience"),
    OpportunityType("operational-efficiency", "Operational Efficiency"),
)

OPPORTUNITY_TYPE_BY_SLUG: dict[str, OpportunityType] = {
    item.slug: item for item in OPPORTUNITY_TYPES
}
OPPORTUNITY_TYPE_BY_NAME: dict[str, OpportunityType] = {
    item.display_name: item for item in OPPORTUNITY_TYPES
}
OPPORTUNITY_TYPE_NAMES: frozenset[str] = frozenset(OPPORTUNITY_TYPE_BY_NAME)


def is_valid_opportunity_type(name: str) -> bool:
    return name.strip() in OPPORTUNITY_TYPE_BY_NAME
