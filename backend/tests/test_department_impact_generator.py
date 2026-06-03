"""Tests for rule-based Department Impact Generator."""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from xerago_intelligence.taxonomy.department_impact_generator import DepartmentImpactGenerator
from xerago_intelligence.taxonomy.impact_categories import IMPACT_CATEGORY_NAMES
from xerago_intelligence.taxonomy.impact_rules import DEPARTMENT_IMPACT_VERSION, MAX_IMPACT_SUMMARY_LENGTH
from xerago_intelligence.taxonomy.opportunity_types import OPPORTUNITY_TYPE_NAMES
from xerago_intelligence.types.impact import DepartmentImpactInput

_CODEX = dict(
    title="OpenAI launches Codex",
    summary="OpenAI released Codex for AI-assisted software development.",
    why_it_matters="Accelerates enterprise coding workflows and delivery speed.",
    domain="ai-ml",
    signal_type="product-technology",
)


def _input(department_name: str, relevance: int) -> DepartmentImpactInput:
    return DepartmentImpactInput(
        **_CODEX,
        department_name=department_name,
        department_relevance_score=relevance,
    )


def test_codex_ai_engineering_summary() -> None:
    result = DepartmentImpactGenerator().generate(_input("AI Engineering", 90))
    assert result.impact_summary == "Build internal AI coding agent capabilities."
    assert result.impact_category == "AI Coding"
    assert result.opportunity_type == "Innovation"
    assert result.impact_version == DEPARTMENT_IMPACT_VERSION
    assert 0 <= result.department_opportunity_score <= 100
    assert "CAT-" in result.impact_reason
    assert "TPL-AI-ENGINEERING" in result.impact_reason


def test_codex_martech_summary() -> None:
    result = DepartmentImpactGenerator().generate(_input("MarTech", 62))
    assert result.impact_summary == "Accelerate campaign content generation."
    assert result.impact_category in IMPACT_CATEGORY_NAMES
    assert result.opportunity_type in OPPORTUNITY_TYPE_NAMES


def test_codex_sales_summary() -> None:
    result = DepartmentImpactGenerator().generate(_input("Sales", 55))
    assert result.impact_summary == "Reduce proposal creation effort in client engagements."
    assert result.opportunity_type == "Revenue Growth"


def test_summary_length_guard() -> None:
    long_summary = "word " * 200
    result = DepartmentImpactGenerator().generate(
        DepartmentImpactInput(
            title="Vendor update",
            summary=long_summary,
            why_it_matters=long_summary,
            domain="industry-trends",
            signal_type="market-narrative",
            department_name="Strategy & Design",
            department_relevance_score=70,
        )
    )
    assert len(result.impact_summary) <= MAX_IMPACT_SUMMARY_LENGTH
    assert result.impact_summary.endswith(".")


def test_deterministic_output() -> None:
    generator = DepartmentImpactGenerator()
    payload = _input("Digital Analytics", 72)
    first = generator.generate(payload)
    second = generator.generate(payload)
    assert first == second


def test_all_departments_produce_valid_impact() -> None:
    from xerago_intelligence.taxonomy.departments import DEPARTMENTS

    generator = DepartmentImpactGenerator()
    for dept in DEPARTMENTS:
        result = generator.generate(_input(dept.display_name, 65))
        assert result.impact_summary
        assert result.impact_category in IMPACT_CATEGORY_NAMES
        assert result.opportunity_type in OPPORTUNITY_TYPE_NAMES
        assert result.impact_version == DEPARTMENT_IMPACT_VERSION


if __name__ == "__main__":
    test_codex_ai_engineering_summary()
    test_codex_martech_summary()
    test_codex_sales_summary()
    test_summary_length_guard()
    test_deterministic_output()
    test_all_departments_produce_valid_impact()
    print("All department impact generator tests passed.")
