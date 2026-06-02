"""Enrichment payload types (shared across AI and DB layers)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EnrichmentPayload:
    """Structured fields produced by the enrichment LLM."""

    summary: str
    why_it_matters: str
    domain: str
    signal_type: str
