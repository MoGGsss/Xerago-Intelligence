"""Centralized department intelligence mapping (re-exports)."""

from xerago_intelligence.taxonomy.department_mapper import (
    DepartmentMapper,
    DepartmentMappingInput,
    DepartmentMappingRecord,
    DepartmentMappingResult,
    DepartmentScore,
    department_for_domain,
    primary_department,
)
from xerago_intelligence.taxonomy.department_rules import DEPARTMENT_MAPPING_VERSION
from xerago_intelligence.taxonomy.departments import (
    DEPARTMENT_CONSOLIDATION_VERSION,
    DEPARTMENT_NAME_ALIASES,
    DEPARTMENT_SLUG_ALIASES,
    DEPARTMENTS,
    DEPARTMENT_NAMES,
    canonical_department_name,
    is_valid_department,
    resolve_department_slug,
)

__all__ = [
    "DEPARTMENT_CONSOLIDATION_VERSION",
    "DEPARTMENTS",
    "DEPARTMENT_MAPPING_VERSION",
    "DEPARTMENT_NAME_ALIASES",
    "DEPARTMENT_NAMES",
    "DEPARTMENT_SLUG_ALIASES",
    "DepartmentMapper",
    "DepartmentMappingInput",
    "DepartmentMappingRecord",
    "DepartmentMappingResult",
    "DepartmentScore",
    "canonical_department_name",
    "department_for_domain",
    "is_valid_department",
    "primary_department",
    "resolve_department_slug",
]
