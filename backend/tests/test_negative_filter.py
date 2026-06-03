"""Tests for negative intelligence filter."""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from xerago_intelligence.filtering.negative_filter import NegativeFilter
from xerago_intelligence.filtering.negative_scorer import (
    NegativeFilterInput,
    NegativeScorer,
)


def test_salesforce_does_not_match_sale_keyword() -> None:
    result = NegativeFilter().evaluate(
        title="Salesforce expands Marketing Cloud capabilities",
        raw_content="Enterprise sales teams can adopt new AI features.",
    )
    assert result.should_skip is False
    assert "sale" not in result.matched_keywords


def test_celebrity_gossip_skips() -> None:
    result = NegativeFilter().evaluate(
        title="Celebrity gossip about famous actor's new movie",
        raw_content="Entertainment news and cinema rumors spread online.",
    )
    assert result.should_skip is True
    assert result.negative_score >= 5
    assert result.skip_reason is not None
    assert "NEG-FILTER-001" in result.skip_reason


def test_bitcoin_prediction_phrase_skips() -> None:
    result = NegativeFilter().evaluate(
        title="Bitcoin prediction for next quarter",
        raw_content="Analysts share crypto price targets.",
    )
    assert result.should_skip is True
    assert "bitcoin prediction" in result.matched_keywords
    assert "crypto price" in result.matched_keywords


def test_threshold_boundary() -> None:
    scorer = NegativeScorer(skip_threshold=5)
    pass_result = scorer.evaluate(
        NegativeFilterInput(title="Politics in enterprise AI", raw_content="")
    )
    assert pass_result.negative_score == 3
    assert pass_result.should_skip is False


if __name__ == "__main__":
    test_salesforce_does_not_match_sale_keyword()
    test_celebrity_gossip_skips()
    test_bitcoin_prediction_phrase_skips()
    test_threshold_boundary()
    print("All negative filter tests passed.")
