"""Schema tests for RSS source registry API."""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from datetime import datetime, timezone

from xerago_intelligence.api.schemas.sources import (
    RssSourceItem,
    SourceStatsItem,
    SourceStatsResponse,
)
from xerago_intelligence.ingest.source_catalog import PHASE_8_RSS_SOURCES


def test_phase8_catalog_has_nineteen_sources() -> None:
    assert len(PHASE_8_RSS_SOURCES) == 19
    tiers = {seed.source_tier for seed in PHASE_8_RSS_SOURCES}
    assert tiers == {1, 2, 3}


def test_source_stats_response_model() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    item = SourceStatsItem(
        source_id="openai-blog",
        source_name="OpenAI",
        source_tier=1,
        active_flag=True,
        last_health_status="healthy",
        total_artifacts=10,
        artifacts_last_24h=2,
        estimated_daily_articles=2.0,
    )
    payload = SourceStatsResponse(
        sources=[item],
        active_source_count=1,
        total_artifacts=10,
        artifacts_last_24h=2,
        estimated_daily_articles_total=2.0,
    )
    assert payload.sources[0].source_id == "openai-blog"
    assert "deduplication" in payload.duplicate_protection.lower()


def test_rss_source_item_tier_bounds() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    row = RssSourceItem(
        source_id="hf-blog",
        source_name="HuggingFace",
        source_url="https://huggingface.co/blog",
        rss_url="https://huggingface.co/blog/feed.xml",
        source_tier=1,
        active_flag=True,
        failure_count=0,
        last_health_status=None,
        last_success_at=now,
        last_failure_at=None,
        last_run_at=now,
    )
    assert row.source_tier == 1
