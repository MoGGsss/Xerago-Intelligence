"""Taxonomy helpers."""

from xerago_intelligence.taxonomy.department_mapping import (
    DEPARTMENT_CONSOLIDATION_VERSION,
    DEPARTMENT_MAPPING_VERSION,
    DEPARTMENT_NAME_ALIASES,
    DEPARTMENT_NAMES,
    DEPARTMENT_SLUG_ALIASES,
    DEPARTMENTS,
    DepartmentMapper,
    DepartmentMappingInput,
    DepartmentMappingResult,
    DepartmentScore,
    canonical_department_name,
    department_for_domain,
    is_valid_department,
    primary_department,
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
    "DepartmentMappingResult",
    "DepartmentScore",
    "canonical_department_name",
    "department_for_domain",
    "is_valid_department",
    "primary_department",
    "resolve_department_slug",
]
