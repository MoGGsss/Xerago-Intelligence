"""Department Impact Engine rule matrices — single source of truth."""

from __future__ import annotations

from dataclasses import dataclass

from xerago_intelligence.taxonomy.impact_categories import IMPACT_CATEGORY_NAMES
from xerago_intelligence.taxonomy.opportunity_types import OPPORTUNITY_TYPE_NAMES

DEPARTMENT_IMPACT_VERSION = "dept_impact_v2.0.0"
MAX_IMPACT_SUMMARY_LENGTH = 120
GLOBAL_FALLBACK_CATEGORY = "Workflow Automation"
GLOBAL_FALLBACK_OPPORTUNITY = "Operational Efficiency"


@dataclass(frozen=True)
class DepartmentImpactProfile:
    default_category: str
    default_opportunity: str
    summary_default: str
    summary_by_signal: tuple[tuple[str, str], ...] = ()
    category_by_signal: tuple[tuple[str, str], ...] = ()
    opportunity_by_signal: tuple[tuple[str, str], ...] = ()


CATEGORY_KEYWORD_RULES: tuple[tuple[tuple[str, ...], str, str], ...] = (
    (("codex", "copilot", "codegen", "coding agent"), "AI Coding", "CAT-KW-AI-CODE"),
    (("agentic", "autonomous agent", "ai agent", "langgraph"), "Agentic AI", "CAT-KW-AGENT"),
    (("campaign", "email marketing", "marketo", "unica"), "Campaign Automation", "CAT-KW-CAMP"),
    (("personalization", "recommendation engine"), "Personalization", "CAT-KW-PERS"),
    (("forecast", "predictive model", "propensity"), "Forecasting", "CAT-KW-FCST"),
    (("lead score", "lead scoring", "scoring model"), "Lead Scoring", "CAT-KW-LEAD"),
    (("customer support", "service cloud", "helpdesk"), "Customer Support", "CAT-KW-SUPPORT"),
    (("knowledge base", "documentation", "rag"), "Knowledge Management", "CAT-KW-KM"),
    (("compliance", "regulation", "gdpr", "privacy"), "Governance", "CAT-KW-GOV"),
    (("security", "cve", "vulnerability", "breach"), "Security", "CAT-KW-SEC"),
    (("content generation", "copywriting", "generative content"), "Content Generation", "CAT-KW-CONTENT"),
    (("analytics", "attribution", "measurement", "bi "), "Analytics", "CAT-KW-ANALYTICS"),
    (("workflow", "orchestration", "rpa"), "Workflow Automation", "CAT-KW-WORKFLOW"),
)

DOMAIN_CATEGORY_DEFAULTS: dict[str, tuple[str, str]] = {
    "ai-ml": ("AI Coding", "CAT-DOM-AIML"),
    "enterprise-ai": ("Agentic AI", "CAT-DOM-ENTAI"),
    "martech": ("Campaign Automation", "CAT-DOM-MARTECH"),
    "personalization": ("Personalization", "CAT-DOM-PERS"),
    "analytics": ("Analytics", "CAT-DOM-ANALYTICS"),
    "automation": ("Workflow Automation", "CAT-DOM-AUTO"),
    "customer-experience": ("Customer Support", "CAT-DOM-CX"),
    "data-engineering": ("Analytics", "CAT-DOM-DE"),
    "cloud-platforms": ("Workflow Automation", "CAT-DOM-CLOUD"),
    "research-signals": ("Knowledge Management", "CAT-DOM-RESEARCH"),
    "industry-trends": ("Forecasting", "CAT-DOM-INDUSTRY"),
    "open-source-ecosystem": ("AI Coding", "CAT-DOM-OSS"),
}

SIGNAL_CATEGORY_DEFAULTS: dict[str, tuple[str, str]] = {
    "product-technology": ("AI Coding", "CAT-SIG-PROD"),
    "go-to-market": ("Campaign Automation", "CAT-SIG-GTM"),
    "partnership-ecosystem": ("Workflow Automation", "CAT-SIG-PARTNER"),
    "research-innovation": ("Knowledge Management", "CAT-SIG-RESEARCH"),
    "regulatory-trust": ("Governance", "CAT-SIG-REG"),
    "operational-incident": ("Security", "CAT-SIG-INCIDENT"),
    "market-narrative": ("Forecasting", "CAT-SIG-MARKET"),
    "competitive-landscape": ("Analytics", "CAT-SIG-COMP"),
}

DEPARTMENT_CATEGORY_BIAS: dict[str, tuple[str, str]] = {
    "ai-engineering": ("AI Coding", "CAT-DEPT-AI"),
    "martech-campaign-services": ("Campaign Automation", "CAT-DEPT-MARTECH"),
    "digital-analytics": ("Analytics", "CAT-DEPT-DA"),
    "content-digital-marketing": ("Content Generation", "CAT-DEPT-CDM"),
    "sales": ("Lead Scoring", "CAT-DEPT-SALES"),
    "account-management": ("Governance", "CAT-DEPT-AM"),
    "xerago-securities": ("Security", "CAT-DEPT-SEC"),
    "digital-operations": ("Security", "CAT-DEPT-DO"),
    "strategy-design-innovation": ("Forecasting", "CAT-DEPT-SDI"),
}

SIGNAL_OPPORTUNITY_DEFAULTS: dict[str, tuple[str, str]] = {
    "go-to-market": ("Revenue Growth", "OPP-SIG-GTM"),
    "product-technology": ("Innovation", "OPP-SIG-PROD"),
    "partnership-ecosystem": ("Revenue Growth", "OPP-SIG-PARTNER"),
    "research-innovation": ("Innovation", "OPP-SIG-RESEARCH"),
    "regulatory-trust": ("Compliance", "OPP-SIG-REG"),
    "operational-incident": ("Risk Management", "OPP-SIG-INCIDENT"),
    "market-narrative": ("Innovation", "OPP-SIG-MARKET"),
    "competitive-landscape": ("Revenue Growth", "OPP-SIG-COMP"),
}

DOMAIN_OPPORTUNITY_DEFAULTS: dict[str, tuple[str, str]] = {
    "ai-ml": ("Innovation", "OPP-DOM-AIML"),
    "enterprise-ai": ("Innovation", "OPP-DOM-ENTAI"),
    "martech": ("Productivity", "OPP-DOM-MARTECH"),
    "personalization": ("Customer Experience", "OPP-DOM-PERS"),
    "analytics": ("Operational Efficiency", "OPP-DOM-ANALYTICS"),
    "automation": ("Automation", "OPP-DOM-AUTO"),
    "customer-experience": ("Customer Experience", "OPP-DOM-CX"),
    "data-engineering": ("Operational Efficiency", "OPP-DOM-DE"),
    "cloud-platforms": ("Cost Reduction", "OPP-DOM-CLOUD"),
    "research-signals": ("Innovation", "OPP-DOM-RESEARCH"),
    "industry-trends": ("Innovation", "OPP-DOM-INDUSTRY"),
    "open-source-ecosystem": ("Innovation", "OPP-DOM-OSS"),
}

DEPARTMENT_OPPORTUNITY_BIAS: dict[str, tuple[str, str]] = {
    "ai-engineering": ("Innovation", "OPP-DEPT-AI"),
    "martech-campaign-services": ("Productivity", "OPP-DEPT-MARTECH"),
    "digital-analytics": ("Operational Efficiency", "OPP-DEPT-DA"),
    "content-digital-marketing": ("Customer Experience", "OPP-DEPT-CDM"),
    "sales": ("Revenue Growth", "OPP-DEPT-SALES"),
    "account-management": ("Compliance", "OPP-DEPT-AM"),
    "xerago-securities": ("Risk Management", "OPP-DEPT-SEC"),
    "digital-operations": ("Automation", "OPP-DEPT-DO"),
    "solutions": ("Customer Experience", "OPP-DEPT-SOL"),
    "strategy-design-innovation": ("Innovation", "OPP-DEPT-SDI"),
}

OPPORTUNITY_TYPE_SCORE_WEIGHT: dict[str, int] = {
    "Revenue Growth": 12,
    "Productivity": 10,
    "Cost Reduction": 9,
    "Automation": 11,
    "Compliance": 8,
    "Risk Management": 9,
    "Innovation": 12,
    "Customer Experience": 10,
    "Employee Experience": 8,
    "Operational Efficiency": 9,
}

DEPARTMENT_IMPACT_PROFILES: dict[str, DepartmentImpactProfile] = {
    "ai-engineering": DepartmentImpactProfile(
        default_category="AI Coding",
        default_opportunity="Innovation",
        summary_default="Build internal AI {capability} capabilities.",
        summary_by_signal=(("product-technology", "Build internal AI {capability} capabilities."),),
        category_by_signal=(("product-technology", "AI Coding"),),
        opportunity_by_signal=(("product-technology", "Innovation"),),
    ),
    "martech-campaign-services": DepartmentImpactProfile(
        default_category="Campaign Automation",
        default_opportunity="Productivity",
        summary_default="Accelerate {content_type} generation for campaigns.",
        summary_by_signal=(
            ("product-technology", "Accelerate campaign content generation."),
            ("go-to-market", "Adjust campaign programs for new GTM changes."),
        ),
        category_by_signal=(
            ("product-technology", "Content Generation"),
            ("go-to-market", "Campaign Automation"),
        ),
    ),
    "sales": DepartmentImpactProfile(
        default_category="Lead Scoring",
        default_opportunity="Revenue Growth",
        summary_default="Reduce {deliverable} creation effort in client engagements.",
        summary_by_signal=(
            ("product-technology", "Reduce proposal creation effort in client engagements."),
            ("go-to-market", "Align revenue plays with new GTM changes."),
        ),
        category_by_signal=(("product-technology", "Lead Scoring"),),
        opportunity_by_signal=(("go-to-market", "Revenue Growth"),),
    ),
    "digital-analytics": DepartmentImpactProfile(
        default_category="Analytics",
        default_opportunity="Operational Efficiency",
        summary_default="Evaluate new measurement approaches for {topic}.",
        category_by_signal=(("product-technology", "Analytics"),),
    ),
    "content-digital-marketing": DepartmentImpactProfile(
        default_category="Content Generation",
        default_opportunity="Customer Experience",
        summary_default="Scale {content_type} production across client programs.",
        summary_by_signal=(("market-narrative", "Adapt editorial workflows to market narrative shifts."),),
    ),
    "digital-operations": DepartmentImpactProfile(
        default_category="Workflow Automation",
        default_opportunity="Automation",
        summary_default="Automate operational workflows impacted by {topic}.",
        summary_by_signal=(("operational-incident", "Activate incident response for {topic}."),),
    ),
    "solutions": DepartmentImpactProfile(
        default_category="Workflow Automation",
        default_opportunity="Customer Experience",
        summary_default="Assess solution design implications of {product} for client delivery.",
        category_by_signal=(("product-technology", "Agentic AI"),),
        summary_by_signal=(
            ("partnership-ecosystem", "Coordinate partner response to {product} changes."),
        ),
    ),
    "account-management": DepartmentImpactProfile(
        default_category="Governance",
        default_opportunity="Compliance",
        summary_default="Brief key accounts on client impact from {topic}.",
        summary_by_signal=(("regulatory-trust", "Update compliance controls for regulatory changes."),),
    ),
    "xerago-securities": DepartmentImpactProfile(
        default_category="Security",
        default_opportunity="Risk Management",
        summary_default="Assess security risk posture changes from {topic}.",
    ),
    "strategy-design-innovation": DepartmentImpactProfile(
        default_category="Forecasting",
        default_opportunity="Innovation",
        summary_default="Monitor {topic} developments for strategic planning.",
        summary_by_signal=(
            ("market-narrative", "Brief leadership on market narrative shifts."),
            ("research-innovation", "Explore pilot opportunities for {topic} in new offerings."),
        ),
    ),
}

GLOBAL_FALLBACK_PROFILE = DepartmentImpactProfile(
    default_category=GLOBAL_FALLBACK_CATEGORY,
    default_opportunity=GLOBAL_FALLBACK_OPPORTUNITY,
    summary_default="Monitor {topic} developments for departmental readiness.",
)

SUMMARY_VERB_VARIANTS: dict[str, tuple[str, ...]] = {
    "Monitor": ("Track", "Review", "Assess", "Evaluate"),
    "Build": ("Develop", "Expand", "Strengthen", "Advance"),
    "Accelerate": ("Speed up", "Enhance", "Boost", "Advance"),
    "Reduce": ("Lower", "Cut", "Minimize", "Decrease"),
}


def assert_registries_aligned() -> None:
    """Validate rule constants reference registered taxonomy values."""
    for _keywords, category, _rule_id in CATEGORY_KEYWORD_RULES:
        if category not in IMPACT_CATEGORY_NAMES:
            raise ValueError(f"Unknown impact category in rules: {category}")
    for category, _rule_id in DOMAIN_CATEGORY_DEFAULTS.values():
        if category not in IMPACT_CATEGORY_NAMES:
            raise ValueError(f"Unknown impact category in domain rules: {category}")
    for opportunity in OPPORTUNITY_TYPE_SCORE_WEIGHT:
        if opportunity not in OPPORTUNITY_TYPE_NAMES:
            raise ValueError(f"Unknown opportunity type in rules: {opportunity}")


assert_registries_aligned()
