"""Strategic scoring weights and lookup tables (Sprint 4)."""

from __future__ import annotations

DOMAIN_WEIGHTS: dict[str, int] = {
    "research-signals": 20,
    "ai-platforms": 25,
    "enterprise-ai": 25,
    "security": 20,
    "customer-experience": 15,
}

SIGNAL_WEIGHTS: dict[str, int] = {
    "research-innovation": 20,
    "product-launch": 25,
    "partnership": 15,
    "acquisition": 20,
    "security-update": 15,
}

# Map taxonomy slugs from enrichment to scoring keys.
DOMAIN_ALIASES: dict[str, str] = {
    "cloud-platforms": "ai-platforms",
    "ai-ml": "ai-platforms",
}

SIGNAL_ALIASES: dict[str, str] = {
    "product-technology": "product-launch",
    "partnership-ecosystem": "partnership",
    "regulatory-trust": "security-update",
    "operational-incident": "security-update",
}

CONFIDENCE_MULTIPLIER = 0.3

RECENCY_0_7_DAYS = 15
RECENCY_8_30_DAYS = 10
RECENCY_31_90_DAYS = 5
RECENCY_OLDER = 0

PRIORITY_LOW = "LOW"
PRIORITY_MEDIUM = "MEDIUM"
PRIORITY_HIGH = "HIGH"
PRIORITY_CRITICAL = "CRITICAL"

PRIORITY_THRESHOLDS: tuple[tuple[int, str], ...] = (
    (90, PRIORITY_CRITICAL),
    (70, PRIORITY_HIGH),
    (40, PRIORITY_MEDIUM),
    (0, PRIORITY_LOW),
)


def resolve_domain_key(domain: str) -> str:
    normalized = domain.strip().lower()
    if normalized in DOMAIN_WEIGHTS:
        return normalized
    return DOMAIN_ALIASES.get(normalized, normalized)


def resolve_signal_key(signal_type: str) -> str:
    normalized = signal_type.strip().lower()
    if normalized in SIGNAL_WEIGHTS:
        return normalized

    if "/" in normalized:
        _l1, l2 = normalized.split("/", 1)
        l2 = l2.strip()
        if l2 == "acquisition":
            return "acquisition"
        if l2 in ("security-patch", "data-breach", "outage-degradation"):
            return "security-update"

    l1 = normalized.split("/", 1)[0]
    if l1 in SIGNAL_ALIASES:
        return SIGNAL_ALIASES[l1]
    if l1 in SIGNAL_WEIGHTS:
        return l1
    return SIGNAL_ALIASES.get(normalized, l1)


def domain_weight(domain: str) -> int:
    key = resolve_domain_key(domain)
    return DOMAIN_WEIGHTS.get(key, 0)


def signal_weight(signal_type: str) -> int:
    key = resolve_signal_key(signal_type)
    return SIGNAL_WEIGHTS.get(key, 0)


def recency_points(age_days: int) -> int:
    if age_days <= 7:
        return RECENCY_0_7_DAYS
    if age_days <= 30:
        return RECENCY_8_30_DAYS
    if age_days <= 90:
        return RECENCY_31_90_DAYS
    return RECENCY_OLDER


def priority_for_score(strategic_score: int) -> str:
    score = max(0, min(100, strategic_score))
    for threshold, label in PRIORITY_THRESHOLDS:
        if score >= threshold:
            return label
    return PRIORITY_LOW
