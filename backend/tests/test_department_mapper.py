"""Tests for department mapping."""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from xerago_intelligence.taxonomy.department_mapper import (
    DepartmentMapper,
    DepartmentMappingInput,
)
from xerago_intelligence.taxonomy.department_rules import DEPARTMENT_MAPPING_VERSION
from xerago_intelligence.taxonomy.departments import DEPARTMENTS, is_valid_department


def test_all_departments_registered() -> None:
    assert len(DEPARTMENTS) == 23
    for dept in DEPARTMENTS:
        assert is_valid_department(dept.display_name)


def test_martech_domain_maps_multiple_departments() -> None:
    result = DepartmentMapper().compute(
        DepartmentMappingInput(
            domain="martech",
            signal_type="partnership-ecosystem",
            summary="Salesforce announces new Marketing Cloud integration.",
            why_it_matters="Partner ecosystem shift affects campaign delivery.",
            confidence_score=80,
            title="Salesforce integration update",
        )
    )
    names = {item.department_name for item in result.departments}
    assert "MarTech" in names
    assert "Content" in names
    assert len(result.departments) <= 5
    assert result.departments[0].department_relevance_score >= result.departments[-1].department_relevance_score


def test_fallback_when_no_threshold_met() -> None:
    result = DepartmentMapper().compute(
        DepartmentMappingInput(
            domain="unknown-domain",
            signal_type="unknown-signal",
            summary="Generic text.",
            why_it_matters="Minimal impact.",
            confidence_score=10,
        )
    )
    assert len(result.departments) == 1
    assert result.departments[0].department_name == "Strategy & Design"


def test_mapping_version_is_v1_3_1() -> None:
    assert DEPARTMENT_MAPPING_VERSION == "dept_map_v1.3.1"


def test_martech_gtm_article_maps_to_sales() -> None:
    result = DepartmentMapper().compute(
        DepartmentMappingInput(
            domain="martech",
            signal_type="product-technology",
            summary="Customer success teams adopt go-to-market playbook for account executive growth.",
            why_it_matters="GTM alignment improves revenue outcomes.",
            confidence_score=100,
            title="Martech customer success GTM update",
        )
    )
    names = {item.department_name for item in result.departments}
    assert "Sales" in names


def test_cloud_platforms_devops_maps_to_operations() -> None:
    result = DepartmentMapper().compute(
        DepartmentMappingInput(
            domain="cloud-platforms",
            signal_type="product-technology",
            summary="Enterprise devops deployment improves observability after outage remediation.",
            why_it_matters="Operations teams need help desk ticketing integration.",
            confidence_score=100,
            title="Cloud devops observability deployment",
        )
    )
    names = {item.department_name for item in result.departments}
    assert "Operations" in names


def test_research_signals_data_analysis_maps_to_digital_analytics() -> None:
    result = DepartmentMapper().compute(
        DepartmentMappingInput(
            domain="research-signals",
            signal_type="research-innovation",
            summary="New benchmark evaluation for time series data analysis and business intelligence metrics.",
            why_it_matters="Research teams need rigorous statistical evaluation.",
            confidence_score=100,
            title="Research signals data analysis benchmark",
        )
    )
    names = {item.department_name for item in result.departments}
    assert "Digital Analytics" in names


def test_salesforce_article_maps_to_sales() -> None:
    result = DepartmentMapper().compute(
        DepartmentMappingInput(
            domain="customer-experience",
            signal_type="go-to-market",
            summary="Salesforce CRM update improves revenue pipeline and deal velocity.",
            why_it_matters="Sales teams need forecasting and opportunity management.",
            confidence_score=100,
            title="Salesforce CRM revenue pipeline",
        )
    )
    names = {item.department_name for item in result.departments}
    assert "Sales" in names
    sales = next(item for item in result.departments if item.department_name == "Sales")
    assert sales.department_relevance_score >= 40


def test_ibm_operations_article_maps_to_operations() -> None:
    result = DepartmentMapper().compute(
        DepartmentMappingInput(
            domain="automation",
            signal_type="operational-incident",
            summary="IBM expands service management and workflow automation for enterprise operations.",
            why_it_matters="Operations teams must optimize infrastructure support processes.",
            confidence_score=100,
            title="IBM operations workflow automation",
        )
    )
    names = {item.department_name for item in result.departments}
    assert "Operations" in names


def test_analytics_article_maps_to_digital_analytics() -> None:
    result = DepartmentMapper().compute(
        DepartmentMappingInput(
            domain="analytics",
            signal_type="product-technology",
            summary="New measurement and attribution dashboard for customer analytics reporting.",
            why_it_matters="Teams need experimentation insights and a/b testing on the analytics platform.",
            confidence_score=100,
            title="Attribution dashboard and customer analytics",
        )
    )
    names = {item.department_name for item in result.departments}
    assert "Digital Analytics" in names
    analytics = next(
        item for item in result.departments if item.department_name == "Digital Analytics"
    )
    assert analytics.department_relevance_score >= 40


def test_generic_ai_article_maps_to_ai_engineering_only() -> None:
    result = DepartmentMapper().compute(
        DepartmentMappingInput(
            domain="ai-ml",
            signal_type="research-innovation",
            summary="New transformer architecture improves inference latency and model scaling.",
            why_it_matters="Engineering teams can deploy faster training pipelines.",
            confidence_score=50,
            title="Transformer inference scaling",
        )
    )
    names = [item.department_name for item in result.departments]
    assert names == ["AI Engineering"]


def test_martech_domain_maps_to_content() -> None:
    result = DepartmentMapper().compute(
        DepartmentMappingInput(
            domain="martech",
            signal_type="product-technology",
            summary="Adobe launches AI content generation for campaign workflows.",
            why_it_matters="Marketing teams can scale creative generation.",
            confidence_score=100,
            title="Adobe content generation update",
        )
    )
    names = {item.department_name for item in result.departments}
    assert "Content" in names
    content = next(item for item in result.departments if item.department_name == "Content")
    assert content.department_relevance_score >= 40


def test_industry_trends_domain_maps_to_content() -> None:
    result = DepartmentMapper().compute(
        DepartmentMappingInput(
            domain="industry-trends",
            signal_type="market-narrative",
            summary="Industry editorial trends reshape marketing content strategy.",
            why_it_matters="Content teams must adapt editorial workflows.",
            confidence_score=100,
            title="Editorial content trends report",
        )
    )
    names = {item.department_name for item in result.departments}
    assert "Content" in names


def test_enterprise_ai_domain_does_not_map_to_content() -> None:
    result = DepartmentMapper().compute(
        DepartmentMappingInput(
            domain="enterprise-ai",
            signal_type="product-technology",
            summary="Enterprise content governance for AI model deployment.",
            why_it_matters="Content security controls for enterprise AI.",
            confidence_score=100,
            title="OpenAI enterprise content governance",
        )
    )
    names = {item.department_name for item in result.departments}
    assert "Content" not in names


if __name__ == "__main__":
    test_all_departments_registered()
    test_martech_domain_maps_multiple_departments()
    test_fallback_when_no_threshold_met()
    print("All department mapper tests passed.")
