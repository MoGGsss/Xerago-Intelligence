"""Tests for DepartmentMappingService impact integration."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from xerago_intelligence.mapping.department_service import DepartmentMappingService
from xerago_intelligence.taxonomy.department_mapper import (
    DepartmentMappingInput,
    DepartmentMappingResult,
    DepartmentScore,
)
from xerago_intelligence.taxonomy.department_rules import DEPARTMENT_MAPPING_VERSION


class _FailingImpactGenerator:
    def generate(self, _inputs):
        raise RuntimeError("impact failed")


def test_records_with_impacts_falls_back_on_generator_failure() -> None:
    service = DepartmentMappingService(MagicMock(), impact_generator=_FailingImpactGenerator())
    inputs = DepartmentMappingInput(
        domain="ai-ml",
        signal_type="product-technology",
        summary="Codex release.",
        why_it_matters="Faster coding.",
        confidence_score=80,
        title="OpenAI launches Codex",
    )
    scores = (DepartmentScore("AI Engineering", 90),)
    records, generated = service._records_with_impacts(inputs, scores)

    assert generated == 0
    assert len(records) == 1
    assert records[0].department_name == "AI Engineering"
    assert records[0].department_relevance_score == 90
    assert records[0].impact_summary is None


def test_records_with_impacts_populates_fields() -> None:
    service = DepartmentMappingService(MagicMock())
    inputs = DepartmentMappingInput(
        domain="ai-ml",
        signal_type="product-technology",
        summary="Codex release.",
        why_it_matters="Faster coding.",
        confidence_score=80,
        title="OpenAI launches Codex",
    )
    scores = (
        DepartmentScore("AI Engineering", 90),
        DepartmentScore("MarTech", 62),
    )
    records, generated = service._records_with_impacts(inputs, scores)

    assert generated == 2
    assert records[0].impact_summary
    assert records[0].impact_category
    assert records[0].opportunity_type
    assert records[0].department_opportunity_score is not None
    assert records[0].impact_reason
    assert records[0].impact_version == "dept_impact_v1.0.0"


def test_backfill_impacts_skips_when_no_mappings() -> None:
    session = MagicMock()
    service = DepartmentMappingService(session)
    service._enrichments = MagicMock()
    service._mappings = MagicMock()
    service._enrichments.get_by_artifact_id.return_value = MagicMock()
    service._mappings.get_by_artifact_id.return_value = []

    assert service.backfill_impacts("artifact-1") == "no_mappings"


def test_map_artifact_return_type_unchanged() -> None:
    """DepartmentMappingResult still exposes DepartmentScore tuples only."""
    result = DepartmentMappingResult(
        departments=(DepartmentScore("Sales", 55),),
        mapping_version=DEPARTMENT_MAPPING_VERSION,
    )
    assert result.departments[0].department_name == "Sales"
    assert not hasattr(result.departments[0], "impact_summary")


if __name__ == "__main__":
    test_records_with_impacts_falls_back_on_generator_failure()
    test_records_with_impacts_populates_fields()
    test_map_artifact_return_type_unchanged()
    print("All department mapping service tests passed.")
