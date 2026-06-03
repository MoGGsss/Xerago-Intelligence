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
    DEPARTMENTS,
    DEPARTMENT_NAMES,
    is_valid_department,
)

__all__ = [
    "DEPARTMENTS",
    "DEPARTMENT_MAPPING_VERSION",
    "DEPARTMENT_NAMES",
    "DepartmentMapper",
    "DepartmentMappingInput",
    "DepartmentMappingRecord",
    "DepartmentMappingResult",
    "DepartmentScore",
    "department_for_domain",
    "is_valid_department",
    "primary_department",
]
