"""Global negative intelligence keywords and phrases."""

from __future__ import annotations

NEGATIVE_FILTER_VERSION = "neg_filter_v1.0.0"
NEGATIVE_FILTER_RULE_ID = "NEG-FILTER-001"

# Single terms matched with word boundaries.
NEGATIVE_KEYWORDS: tuple[str, ...] = (
    "celebrity",
    "actor",
    "actress",
    "movie",
    "cinema",
    "football",
    "cricket",
    "soccer",
    "lottery",
    "betting",
    "gambling",
    "coupon",
    "discount",
    "sale",
    "giveaway",
    "memecoin",
    "politics",
    "rumor",
    "gossip",
)

# Multi-word phrases matched as substrings (normalized whitespace).
NEGATIVE_PHRASES: tuple[str, ...] = (
    "crypto price",
    "bitcoin prediction",
)

# Lowercase substrings that prevent a single-keyword false positive for "sale".
SALE_ALLOWLIST: tuple[str, ...] = (
    "salesforce",
    "sales cloud",
    "sales program",
    "sales team",
    "upsell",
    "cross-sell",
)
