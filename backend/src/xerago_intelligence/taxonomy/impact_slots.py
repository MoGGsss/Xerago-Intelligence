"""Deterministic slot extraction from enrichment text (no LLM)."""

from __future__ import annotations

# (keywords, slot_value) — first match wins
CAPABILITY_SLOTS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("codex", "copilot", "codegen", "coding agent", "code assistant"), "coding agent"),
    (("agentic", "autonomous agent", "ai agent", "agent framework"), "agent"),
    (("api", "sdk", "integration"), "integration"),
    (("model", "llm", "foundation model", "gpt"), "model"),
    (("automation", "workflow", "orchestration"), "automation"),
)

CONTENT_TYPE_SLOTS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("campaign", "email marketing", "marketo", "unica"), "campaign content"),
    (("personalization", "recommendation", "targeting"), "personalized content"),
    (("blog", "editorial", "copy"), "marketing content"),
)

DELIVERABLE_SLOTS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("proposal", "rfp", "pitch deck"), "proposal"),
    (("brief", "sow", "statement of work"), "client brief"),
    (("report", "dashboard"), "client report"),
)

PRODUCT_ENTITIES: tuple[str, ...] = (
    "openai",
    "salesforce",
    "adobe",
    "ibm",
    "microsoft",
    "google",
    "anthropic",
    "marketo",
    "agentforce",
    "firefly",
    "watsonx",
)

TOPIC_STOPWORDS: frozenset[str] = frozenset(
    {
        "the",
        "a",
        "an",
        "for",
        "with",
        "and",
        "to",
        "of",
        "in",
        "on",
        "new",
        "latest",
        "announces",
        "launches",
        "release",
        "update",
    }
)


def _text_blob(title: str, summary: str, why_it_matters: str) -> str:
    return " ".join([title, summary, why_it_matters]).lower()


def _first_match(text: str, rules: tuple[tuple[tuple[str, ...], str], ...], default: str) -> str:
    for keywords, value in rules:
        if any(keyword in text for keyword in keywords):
            return value
    return default


def extract_capability(title: str, summary: str, why_it_matters: str) -> str:
    return _first_match(_text_blob(title, summary, why_it_matters), CAPABILITY_SLOTS, "automation")


def extract_content_type(title: str, summary: str, why_it_matters: str) -> str:
    return _first_match(_text_blob(title, summary, why_it_matters), CONTENT_TYPE_SLOTS, "campaign content")


def extract_deliverable(title: str, summary: str, why_it_matters: str) -> str:
    return _first_match(_text_blob(title, summary, why_it_matters), DELIVERABLE_SLOTS, "proposal")


def extract_product(title: str, summary: str, why_it_matters: str) -> str:
    text = _text_blob(title, summary, why_it_matters)
    for entity in PRODUCT_ENTITIES:
        if entity in text:
            return entity.title()
    words = [word for word in title.split() if word.lower() not in TOPIC_STOPWORDS]
    if words:
        return words[0]
    return "this development"


def extract_topic(title: str, summary: str, why_it_matters: str, *, max_words: int = 4) -> str:
    source = summary.strip() or title.strip() or why_it_matters.strip()
    words = [
        word
        for word in source.replace(",", " ").split()
        if word and word.lower() not in TOPIC_STOPWORDS
    ]
    if not words:
        return "emerging capabilities"
    phrase = " ".join(words[:max_words])
    return phrase[:48].rstrip(".,;:")
