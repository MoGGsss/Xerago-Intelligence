"""Versioned enrichment prompts."""

from __future__ import annotations

PROMPT_VERSION = "enrich_v2"

DOMAIN_SLUGS = (
    "ai-ml",
    "customer-experience",
    "martech",
    "analytics",
    "personalization",
    "automation",
    "enterprise-ai",
    "open-source-ecosystem",
    "research-signals",
    "industry-trends",
    "cloud-platforms",
    "data-engineering",
)

SIGNAL_TYPES = (
    "product-technology",
    "go-to-market",
    "partnership-ecosystem",
    "research-innovation",
    "regulatory-trust",
    "competitive-landscape",
    "operational-incident",
    "market-narrative",
)


def build_enrichment_prompt(
    *,
    title: str,
    source_id: str,
    url: str,
    published_at: str,
    body: str | None,
) -> str:
    """Build the LLM prompt that must return JSON only (plain text, no Ollama JSON mode)."""
    content = (body or "").strip()
    if len(content) > 8000:
        content = content[:8000] + "\n…[truncated]"

    domains_list = ", ".join(DOMAIN_SLUGS)
    signal_list = ", ".join(SIGNAL_TYPES)

    return f"""You are an enterprise technology intelligence analyst for Xerago.

Analyze the article below.

Return ONLY valid JSON. Your entire reply must be a single JSON object and nothing else.

Example shape:
{{
  "summary": "...",
  "why_it_matters": "...",
  "domain": "...",
  "signal_type": "..."
}}

Rules:
- No markdown
- No code fences
- No explanations
- No thinking
- No text before the opening {{
- No text after the closing }}

Required keys (all string values):
- summary: 2-4 sentences, factual, max 600 characters
- why_it_matters: 2-3 sentences on business impact for Xerago and clients, max 800 characters
- domain: exactly one slug from: {domains_list}
- signal_type: exactly one slug from: {signal_list}

Article metadata:
- source_id: {source_id}
- title: {title}
- url: {url}
- published_at: {published_at}

Article body:
{content if content else "(no body text — infer from title and metadata)"}"""
