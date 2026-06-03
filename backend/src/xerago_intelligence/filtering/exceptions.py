"""Filtering layer exceptions."""

from __future__ import annotations

from xerago_intelligence.filtering.negative_scorer import NegativeFilterResult


class EnrichmentSkippedError(Exception):
    """Raised when an artifact fails pre-enrichment negative filtering."""

    def __init__(self, artifact_id: str, result: NegativeFilterResult) -> None:
        self.artifact_id = artifact_id
        self.result = result
        super().__init__(result.skip_reason or "Enrichment skipped by negative filter")
