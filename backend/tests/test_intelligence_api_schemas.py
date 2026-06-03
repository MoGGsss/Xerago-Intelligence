"""Tests for intelligence API schema backward compatibility."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from xerago_intelligence.api.schemas.intelligence import DepartmentMappingItem, IntelligenceItem


def test_department_mapping_item_legacy_shape() -> None:
    item = DepartmentMappingItem(
        department_name="MarTech",
        department_relevance_score=72,
    )
    payload = item.model_dump()
    assert payload["department_name"] == "MarTech"
    assert payload["department_relevance_score"] == 72
    assert payload["impact_summary"] is None
    assert payload["impact_version"] is None


def test_department_mapping_item_with_impact_fields() -> None:
    item = DepartmentMappingItem(
        department_name="AI Engineering",
        department_relevance_score=90,
        impact_summary="Build internal AI coding agent capabilities.",
        impact_category="AI Coding",
        opportunity_type="Innovation",
        department_opportunity_score=91,
        impact_reason="category=CAT-DEPT-AI",
        impact_version="dept_impact_v1.0.0",
    )
    serialized = json.loads(item.model_dump_json())
    assert serialized["impact_category"] == "AI Coding"
    assert serialized["impact_version"] == "dept_impact_v1.0.0"


def test_intelligence_item_preserves_top_level_fields() -> None:
    now = datetime.now(timezone.utc)
    item = IntelligenceItem(
        artifact_id="abc-123",
        title="OpenAI launches Codex",
        url="https://example.com/codex",
        published_at=now,
        summary="Codex release.",
        why_it_matters="Faster coding.",
        domain="ai-ml",
        signal_type="product-technology",
        confidence_score=85,
        validation_status="validated",
        strategic_score=78,
        priority_level="HIGH",
        departments=[
            DepartmentMappingItem(
                department_name="AI Engineering",
                department_relevance_score=90,
                impact_summary="Build internal AI coding agent capabilities.",
                impact_category="AI Coding",
                opportunity_type="Innovation",
                department_opportunity_score=91,
                impact_reason="category=CAT-DEPT-AI",
                impact_version="dept_impact_v1.0.0",
            )
        ],
        department="AI Engineering",
    )
    payload = item.model_dump()
    assert payload["artifact_id"] == "abc-123"
    assert payload["department"] == "AI Engineering"
    assert len(payload["departments"]) == 1
    assert payload["departments"][0]["impact_summary"] is not None


if __name__ == "__main__":
    test_department_mapping_item_legacy_shape()
    test_department_mapping_item_with_impact_fields()
    test_intelligence_item_preserves_top_level_fields()
    print("All intelligence API schema tests passed.")
