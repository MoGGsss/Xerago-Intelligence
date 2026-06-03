"""Canonical Xerago department registry."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Department:
    slug: str
    display_name: str


DEPARTMENTS: tuple[Department, ...] = (
    Department("account-management", "Account Management"),
    Department("administration", "Administration"),
    Department("ai-engineering", "AI Engineering"),
    Department("campaign-services", "Campaign Services"),
    Department("content", "Content"),
    Department("digital-analytics", "Digital Analytics"),
    Department("digital-marketing", "Digital Marketing"),
    Department("digital-operations", "Digital Operations"),
    Department("finance-legal", "Finance & Legal"),
    Department("founders-office", "Founder's Office"),
    Department("hr", "HR"),
    Department("it-operations-support", "IT Operations & Support"),
    Department("martech", "MarTech"),
    Department("new-initiatives", "New Initiatives"),
    Department("operations", "Operations"),
    Department("partner-management", "Partner Management"),
    Department("program-management", "Program Management"),
    Department("qc", "QC"),
    Department("revenue-growth", "Revenue Growth"),
    Department("sales", "Sales"),
    Department("solutions", "Solutions"),
    Department("strategy-design", "Strategy & Design"),
    Department("xerago-securities", "Xerago Securities"),
)

DEPARTMENT_BY_SLUG: dict[str, Department] = {d.slug: d for d in DEPARTMENTS}
DEPARTMENT_BY_NAME: dict[str, Department] = {d.display_name: d for d in DEPARTMENTS}
DEPARTMENT_NAMES: frozenset[str] = frozenset(DEPARTMENT_BY_NAME)


def is_valid_department(name: str) -> bool:
    return name.strip() in DEPARTMENT_BY_NAME


def department_slug(name: str) -> str | None:
    dept = DEPARTMENT_BY_NAME.get(name.strip())
    return dept.slug if dept else None
