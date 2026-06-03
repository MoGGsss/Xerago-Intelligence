"""Tests for intelligence query repository department mapping projection."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from xerago_intelligence.db.repositories.intelligence_query_repository import (
    IntelligenceQueryRepository,
)


def test_department_item_from_row_maps_impact_fields() -> None:
    row = MagicMock()
    row.department_name = "Sales"
    row.department_relevance_score = 55
    row.impact_summary = "Reduce proposal creation effort in client engagements."
    row.impact_category = "Lead Scoring"
    row.opportunity_type = "Revenue Growth"
    row.department_opportunity_score = 63
    row.impact_reason = "category=CAT-DEPT-SALES"
    row.impact_version = "dept_impact_v1.0.0"

    item = IntelligenceQueryRepository._department_item_from_row(row)

    assert item.department_name == "Sales"
    assert item.department_relevance_score == 55
    assert item.impact_summary == "Reduce proposal creation effort in client engagements."
    assert item.impact_category == "Lead Scoring"
    assert item.opportunity_type == "Revenue Growth"
    assert item.department_opportunity_score == 63
    assert item.impact_reason == "category=CAT-DEPT-SALES"
    assert item.impact_version == "dept_impact_v1.0.0"


def test_department_item_from_row_null_impact_fields() -> None:
    row = MagicMock()
    row.department_name = "MarTech"
    row.department_relevance_score = 70
    row.impact_summary = None
    row.impact_category = None
    row.opportunity_type = None
    row.department_opportunity_score = None
    row.impact_reason = None
    row.impact_version = None

    item = IntelligenceQueryRepository._department_item_from_row(row)

    assert item.impact_summary is None
    assert item.impact_version is None


if __name__ == "__main__":
    test_department_item_from_row_maps_impact_fields()
    test_department_item_from_row_null_impact_fields()
    print("All intelligence query repository tests passed.")
