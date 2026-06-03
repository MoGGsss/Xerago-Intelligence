"""Schema tests for executive analytics API."""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from xerago_intelligence.api.schemas.analytics import (
    AnalyticsOverviewResponse,
    FeedbackSummary,
    RankedMetricItem,
)


def test_overview_response_defaults() -> None:
    payload = AnalyticsOverviewResponse(
        articles_today=5,
        active_sources=19,
        enriched_articles=120,
        average_strategic_score=72.5,
        feedback_total=10,
        feedback_positive=7,
        feedback_negative=3,
    )
    assert payload.active_sources == 19


def test_feedback_summary_positive_pct() -> None:
    summary = FeedbackSummary(
        total=10,
        positive=7,
        negative=3,
        positive_pct=70.0,
        trends=[],
    )
    assert summary.positive_pct == 70.0


def test_ranked_metric_item() -> None:
    item = RankedMetricItem(label="Marketing", count=12, avg_score=81.2)
    assert item.label == "Marketing"
