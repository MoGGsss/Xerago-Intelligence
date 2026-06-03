"""Pure negative filter evaluation (no persistence)."""

from __future__ import annotations

from xerago_intelligence.filtering.negative_scorer import (
    NegativeFilterInput,
    NegativeFilterResult,
    NegativeScorer,
)


class NegativeFilter:
    """Evaluate artifacts against global negative keyword rules."""

    def __init__(self, *, scorer: NegativeScorer | None = None) -> None:
        self._scorer = scorer or NegativeScorer()

    def evaluate(
        self,
        *,
        title: str,
        raw_content: str | None,
    ) -> NegativeFilterResult:
        return self._scorer.evaluate(
            NegativeFilterInput(title=title, raw_content=raw_content)
        )
