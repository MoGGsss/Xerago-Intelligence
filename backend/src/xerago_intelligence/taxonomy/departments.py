"""Canonical Xerago department registry (10 departments, Phase 1A consolidation)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Department:
    slug: str
    display_name: str


# --- Canonical registry (10) ---

DEPARTMENTS: tuple[Department, ...] = (
    Department("ai-engineering", "AI Engineering"),
    Department("solutions", "Solutions"),
    Department("digital-analytics", "Digital Analytics"),
    Department("strategy-design-innovation", "Strategy, Design & Innovation"),
    Department("digital-operations", "Digital Operations"),
    Department("sales", "Sales"),
    Department("account-management", "Account Management"),
    Department("content-digital-marketing", "Content & Digital Marketing"),
    Department("martech-campaign-services", "MarTech & Campaign Services"),
    Department("xerago-securities", "Xerago Securities"),
)

DEPARTMENT_CONSOLIDATION_VERSION = "dept_consolidation_v2.0.0"

# Legacy slug -> canonical slug (90-day API / filter compatibility)
DEPARTMENT_SLUG_ALIASES: dict[str, str] = {
    "administration": "strategy-design-innovation",
    "campaign-services": "martech-campaign-services",
    "content": "content-digital-marketing",
    "digital-marketing": "content-digital-marketing",
    "finance-legal": "account-management",
    "founders-office": "strategy-design-innovation",
    "hr": "strategy-design-innovation",
    "it-operations-support": "digital-operations",
    "martech": "martech-campaign-services",
    "new-initiatives": "strategy-design-innovation",
    "operations": "digital-operations",
    "partner-management": "sales",
    "program-management": "solutions",
    "qc": "digital-operations",
    "revenue-growth": "sales",
    "strategy-design": "strategy-design-innovation",
}

# Legacy display name -> canonical display name (DB backfill + feedback)
DEPARTMENT_NAME_ALIASES: dict[str, str] = {
    "Administration": "Strategy, Design & Innovation",
    "Campaign Services": "MarTech & Campaign Services",
    "Content": "Content & Digital Marketing",
    "Digital Marketing": "Content & Digital Marketing",
    "Finance & Legal": "Account Management",
    "Founder's Office": "Strategy, Design & Innovation",
    "HR": "Strategy, Design & Innovation",
    "IT Operations & Support": "Digital Operations",
    "MarTech": "MarTech & Campaign Services",
    "New Initiatives": "Strategy, Design & Innovation",
    "Operations": "Digital Operations",
    "Partner Management": "Sales",
    "Program Management": "Solutions",
    "QC": "Digital Operations",
    "Revenue Growth": "Sales",
    "Strategy & Design": "Strategy, Design & Innovation",
}

CANONICAL_BY_SLUG: dict[str, Department] = {d.slug: d for d in DEPARTMENTS}

DEPARTMENT_BY_SLUG: dict[str, Department] = dict(CANONICAL_BY_SLUG)
for alias_slug, canonical_slug in DEPARTMENT_SLUG_ALIASES.items():
    DEPARTMENT_BY_SLUG[alias_slug] = CANONICAL_BY_SLUG[canonical_slug]

DEPARTMENT_BY_NAME: dict[str, Department] = {d.display_name: d for d in DEPARTMENTS}
for alias_name, canonical_name in DEPARTMENT_NAME_ALIASES.items():
    DEPARTMENT_BY_NAME[alias_name] = DEPARTMENT_BY_NAME[canonical_name]

DEPARTMENT_NAMES: frozenset[str] = frozenset(DEPARTMENT_BY_NAME)


def resolve_department_slug(slug: str) -> str | None:
    """Map legacy or canonical slug to canonical slug."""
    normalized = slug.strip().lower()
    if normalized in CANONICAL_BY_SLUG:
        return normalized
    return DEPARTMENT_SLUG_ALIASES.get(normalized)


def canonical_department_name(name: str) -> str | None:
    """Map legacy or canonical display name to canonical display name."""
    stripped = name.strip()
    if stripped in DEPARTMENT_NAME_ALIASES:
        return DEPARTMENT_NAME_ALIASES[stripped]
    dept = DEPARTMENT_BY_NAME.get(stripped)
    if dept is not None and dept.display_name in {d.display_name for d in DEPARTMENTS}:
        return dept.display_name
    return None


def is_valid_department(name: str) -> bool:
    return canonical_department_name(name) is not None


def department_slug(name: str) -> str | None:
    canonical = canonical_department_name(name)
    if canonical is None:
        return None
    return DEPARTMENT_BY_NAME[canonical].slug
