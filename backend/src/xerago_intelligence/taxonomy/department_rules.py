"""Domain and signal weight matrices for department relevance scoring."""

from __future__ import annotations

# Base weights: domain slug -> department slug -> base score (0-100).
# Department slugs are canonical (10-department registry).
DOMAIN_DEPARTMENT_WEIGHTS: dict[str, dict[str, int]] = {
    "ai-ml": {
        "ai-engineering": 90,
        "solutions": 55,
        "strategy-design-innovation": 45,
        "digital-analytics": 40,
    },
    "customer-experience": {
        "solutions": 80,
        "content-digital-marketing": 70,
        "martech-campaign-services": 65,
        "strategy-design-innovation": 55,
        "account-management": 50,
        "sales": 50,
    },
    "martech": {
        "martech-campaign-services": 85,
        "content-digital-marketing": 70,
        "solutions": 45,
        "digital-analytics": 40,
        "sales": 45,
    },
    "analytics": {
        "digital-analytics": 90,
        "martech-campaign-services": 50,
        "strategy-design-innovation": 45,
        "content-digital-marketing": 40,
    },
    "personalization": {
        "martech-campaign-services": 75,
        "content-digital-marketing": 70,
        "solutions": 60,
        "digital-analytics": 50,
        "sales": 40,
    },
    "automation": {
        "ai-engineering": 75,
        "digital-operations": 65,
        "solutions": 50,
    },
    "enterprise-ai": {
        "ai-engineering": 90,
        "solutions": 60,
        "strategy-design-innovation": 50,
        "digital-analytics": 45,
        "digital-operations": 40,
    },
    "open-source-ecosystem": {
        "ai-engineering": 70,
        "digital-operations": 55,
        "strategy-design-innovation": 45,
    },
    "research-signals": {
        "ai-engineering": 75,
        "strategy-design-innovation": 70,
        "digital-analytics": 50,
    },
    "industry-trends": {
        "strategy-design-innovation": 75,
        "content-digital-marketing": 45,
        "sales": 55,
    },
    "cloud-platforms": {
        "digital-operations": 75,
        "solutions": 55,
        "ai-engineering": 45,
    },
    "data-engineering": {
        "digital-analytics": 80,
        "ai-engineering": 60,
        "digital-operations": 50,
    },
}

# Additive boosts: signal L1 slug -> department slug -> boost points.
SIGNAL_DEPARTMENT_BOOSTS: dict[str, dict[str, int]] = {
    "product-technology": {
        "solutions": 15,
        "digital-operations": 10,
        "content-digital-marketing": 12,
        "digital-analytics": 4,
        "sales": 12,
    },
    "go-to-market": {
        "sales": 20,
        "content-digital-marketing": 15,
        "martech-campaign-services": 10,
    },
    "partnership-ecosystem": {
        "sales": 25,
        "account-management": 15,
    },
    "research-innovation": {
        "ai-engineering": 15,
        "strategy-design-innovation": 20,
        "digital-analytics": 4,
    },
    "regulatory-trust": {
        "account-management": 30,
        "xerago-securities": 25,
        "strategy-design-innovation": 15,
    },
    "competitive-landscape": {
        "strategy-design-innovation": 20,
        "sales": 15,
    },
    "operational-incident": {
        "digital-operations": 25,
    },
    "market-narrative": {
        "strategy-design-innovation": 15,
        "content-digital-marketing": 15,
        "sales": 10,
    },
}

# Keyword boosts applied to summary + why_it_matters + title (lowercase match).
KEYWORD_DEPARTMENT_BOOSTS: tuple[tuple[tuple[str, ...], str, int], ...] = (
    (("campaign", "email marketing", "marketo", "unica"), "martech-campaign-services", 10),
    (("partner", "alliance", "integration"), "sales", 10),
    (("adobe", "client", "account"), "account-management", 8),
    (("security", "compliance", "regulation", "privacy"), "account-management", 10),
    (("hire", "talent", "workforce", "hr"), "strategy-design-innovation", 10),
    (
        (
            "content generation",
            "copywriting",
            "blog",
            "editorial",
            "campaign content",
            "social content",
            "marketing content",
            "email content",
            "creative generation",
        ),
        "content-digital-marketing",
        12,
    ),
    (("program", "project", "delivery"), "solutions", 8),
    (("qc", "quality", "testing", "bug"), "digital-operations", 10),
    (
        (
            "salesforce",
            "crm",
            "revenue",
            "pipeline",
            "forecasting",
            "account management",
            "partner ecosystem",
            "customer acquisition",
            "deal velocity",
            "opportunity management",
            "customer success",
            "account executive",
            "gtm",
            "go-to-market",
        ),
        "sales",
        12,
    ),
    (
        (
            "operations",
            "workflow",
            "automation",
            "governance",
            "service management",
            "infrastructure",
            "support",
            "process optimization",
            "servicenow",
            "hcl",
            "microsoft",
            "ibm",
            "devops",
            "observability",
            "deployment",
            "outage",
            "incident response",
            "help desk",
            "ticketing",
        ),
        "digital-operations",
        12,
    ),
    (
        (
            "measurement",
            "attribution",
            "experimentation",
            "forecasting",
            "customer analytics",
            "dashboard",
            "insights",
            "reporting",
            "a/b testing",
            "analytics platform",
            "data analysis",
            "time series",
            "benchmark",
            "evaluation",
            "metrics",
            "business intelligence",
        ),
        "digital-analytics",
        12,
    ),
)

MIN_RELEVANCE_SCORE = 40
MAX_DEPARTMENTS_PER_ARTIFACT = 5
FALLBACK_DEPARTMENT_SLUG = "strategy-design-innovation"
INDUSTRY_TRENDS_FALLBACK_SLUG = "strategy-design-innovation"

DEPARTMENT_MAPPING_VERSION = "dept_map_v2.0.0"
