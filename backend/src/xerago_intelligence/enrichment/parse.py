"""Parse and validate LLM enrichment JSON."""

from __future__ import annotations

import json
import re
from typing import Any

from xerago_intelligence.enrichment.prompts import DOMAIN_SLUGS, SIGNAL_TYPES
from xerago_intelligence.types.enrichment import EnrichmentPayload

_JSON_FENCE_RE = re.compile(
    r"```(?:json)?\s*([\s\S]*?)\s*```",
    re.IGNORECASE,
)


class EnrichmentParseError(ValueError):
    """Raised when LLM output cannot be parsed into EnrichmentPayload."""


def parse_enrichment_json(text: str) -> EnrichmentPayload:
    """Parse model output into a validated EnrichmentPayload."""
    json_text = extract_first_json_object(text)
    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise EnrichmentParseError(f"Invalid JSON from model: {exc}") from exc

    if not isinstance(data, dict):
        raise EnrichmentParseError("Enrichment JSON must be an object")

    # Ignore thinking / chain-of-thought keys if the model emits them.
    data.pop("thinking", None)

    return _validate_payload(data)


def extract_first_json_object(text: str) -> str:
    """
    Extract the first JSON object from model output.

    Supports plain JSON, fenced blocks, and preamble text (e.g. thinking traces).
    """
    stripped = text.strip()
    if not stripped:
        raise EnrichmentParseError("Model output is empty")

    fence_match = _JSON_FENCE_RE.search(stripped)
    if fence_match:
        fenced = fence_match.group(1).strip()
        balanced = _balanced_brace_slice(fenced)
        if balanced:
            return balanced
        if fenced.startswith("{"):
            return fenced

    if stripped.startswith("{"):
        balanced = _balanced_brace_slice(stripped)
        if balanced:
            return balanced

    start = stripped.find("{")
    if start >= 0:
        balanced = _balanced_brace_slice(stripped[start:])
        if balanced:
            return balanced

    raise EnrichmentParseError("No JSON object found in model output")


def _balanced_brace_slice(text: str) -> str | None:
    """Return substring from first ``{`` through its matching ``}``, or None."""
    if not text or text[0] != "{":
        return None

    depth = 0
    in_string = False
    escape = False

    for index, char in enumerate(text):
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[: index + 1]

    return None


def _validate_payload(data: dict[str, Any]) -> EnrichmentPayload:
    required = ("summary", "why_it_matters", "domain", "signal_type")
    missing = [key for key in required if key not in data]
    if missing:
        raise EnrichmentParseError(f"Missing required keys: {', '.join(missing)}")

    summary = _as_nonempty_str(data["summary"], "summary")
    why_it_matters = _as_nonempty_str(data["why_it_matters"], "why_it_matters")
    domain = _as_nonempty_str(data["domain"], "domain")
    signal_type = _as_nonempty_str(data["signal_type"], "signal_type")

    if domain not in DOMAIN_SLUGS:
        raise EnrichmentParseError(
            f"Invalid domain {domain!r}; must be one of: {', '.join(DOMAIN_SLUGS)}"
        )
    if signal_type not in SIGNAL_TYPES:
        raise EnrichmentParseError(
            f"Invalid signal_type {signal_type!r}; "
            f"must be one of: {', '.join(SIGNAL_TYPES)}"
        )

    return EnrichmentPayload(
        summary=summary,
        why_it_matters=why_it_matters,
        domain=domain,
        signal_type=signal_type,
    )


def _as_nonempty_str(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EnrichmentParseError(f"{field} must be a non-empty string")
    return value.strip()
