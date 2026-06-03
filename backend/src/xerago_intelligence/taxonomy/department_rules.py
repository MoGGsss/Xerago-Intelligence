"""Domain and signal weight matrices for department relevance scoring."""

from __future__ import annotations

# Base weights: domain slug -> department slug -> base score (0-100).
DOMAIN_DEPARTMENT_WEIGHTS: dict[str, dict[str, int]] = {
    "ai-ml": {
        "ai-engineering": 90,
        "solutions": 55,
        "new-initiatives": 45,
        "digital-analytics": 40,
    },
    "customer-experience": {
        "solutions": 80,
        "digital-marketing": 70,
        "martech": 65,
        "content": 50,
        "strategy-design": 55,
        "account-management": 50,
        "sales": 50,
    },
    "martech": {
        "martech": 85,
        "digital-marketing": 70,
        "campaign-services": 65,
        "content": 55,
        "solutions": 45,
        "digital-analytics": 40,
        "sales": 45,
    },
    "analytics": {
        "digital-analytics": 90,
        "martech": 50,
        "strategy-design": 45,
        "digital-marketing": 40,
    },
    "personalization": {
        "martech": 75,
        "digital-marketing": 70,
        "solutions": 60,
        "digital-analytics": 50,
        "sales": 40,
    },
    "automation": {
        "ai-engineering": 75,
        "digital-operations": 65,
        "operations": 55,
        "solutions": 50,
    },
    "enterprise-ai": {
        "ai-engineering": 90,
        "solutions": 60,
        "new-initiatives": 50,
        "founders-office": 45,
        "digital-analytics": 45,
        "operations": 40,
    },
    "open-source-ecosystem": {
        "ai-engineering": 70,
        "digital-operations": 55,
        "it-operations-support": 50,
        "new-initiatives": 45,
        "operations": 40,
    },
    "research-signals": {
        "ai-engineering": 75,
        "founders-office": 70,
        "strategy-design": 55,
        "new-initiatives": 50,
        "digital-analytics": 50,
    },
    "industry-trends": {
        "founders-office": 75,
        "strategy-design": 70,
        "content": 45,
        "revenue-growth": 55,
        "sales": 45,
    },
    "cloud-platforms": {
        "it-operations-support": 75,
        "digital-operations": 70,
        "solutions": 55,
        "ai-engineering": 45,
        "operations": 45,
    },
    "data-engineering": {
        "digital-analytics": 80,
        "ai-engineering": 60,
        "it-operations-support": 50,
        "digital-operations": 45,
        "operations": 40,
    },
}

# Additive boosts: signal L1 slug -> department slug -> boost points.
SIGNAL_DEPARTMENT_BOOSTS: dict[str, dict[str, int]] = {
    "product-technology": {
        "solutions": 15,
        "program-management": 10,
        "qc": 10,
        "content": 12,
        "digital-analytics": 4,
        "operations": 5,
        "sales": 12,
    },
    "go-to-market": {
        "revenue-growth": 20,
        "sales": 20,
        "digital-marketing": 15,
        "campaign-services": 10,
        "content": 15,
    },
    "partnership-ecosystem": {
        "partner-management": 25,
        "sales": 15,
        "account-management": 15,
    },
    "research-innovation": {
        "ai-engineering": 15,
        "founders-office": 20,
        "new-initiatives": 15,
        "digital-analytics": 4,
    },
    "regulatory-trust": {
        "finance-legal": 30,
        "xerago-securities": 25,
        "administration": 15,
    },
    "competitive-landscape": {
        "strategy-design": 20,
        "sales": 15,
        "revenue-growth": 15,
        "founders-office": 10,
    },
    "operational-incident": {
        "it-operations-support": 25,
        "digital-operations": 20,
        "qc": 15,
        "operations": 15,
    },
    "market-narrative": {
        "founders-office": 15,
        "strategy-design": 15,
        "content": 15,
        "revenue-growth": 10,
        "sales": 10,
    },
}

# Keyword boosts applied to summary + why_it_matters + title (lowercase match).
KEYWORD_DEPARTMENT_BOOSTS: tuple[tuple[tuple[str, ...], str, int], ...] = (
    (("campaign", "email marketing", "marketo", "unica"), "campaign-services", 10),
    (("partner", "alliance", "integration"), "partner-management", 10),
    (("adobe", "client", "account"), "account-management", 8),
    (("security", "compliance", "regulation", "privacy"), "finance-legal", 10),
    (("hire", "talent", "workforce", "hr"), "hr", 10),
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
        "content",
        12,
    ),
    (("program", "project", "delivery"), "program-management", 8),
    (("qc", "quality", "testing", "bug"), "qc", 10),
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
        "operations",
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
FALLBACK_DEPARTMENT_SLUG = "strategy-design"
INDUSTRY_TRENDS_FALLBACK_SLUG = "founders-office"

DEPARTMENT_MAPPING_VERSION = "dept_map_v1.3.1"
