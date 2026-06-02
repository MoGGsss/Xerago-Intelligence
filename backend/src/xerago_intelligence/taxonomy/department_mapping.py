"""Centralized mapping from intelligence domain to business department."""

from __future__ import annotations

DOMAIN_TO_DEPARTMENT: dict[str, str] = {
    "enterprise-ai": "AI",
    "ai-ml": "AI",
    "research-signals": "Leadership",
    "cloud-platforms": "Cloud",
    "martech": "Marketing",
    "marketing-technology": "Marketing",
    "analytics": "Analytics",
}


def department_for_domain(domain: str | None) -> str | None:
    if not domain:
        return None
    return DOMAIN_TO_DEPARTMENT.get(domain.strip().lower())
