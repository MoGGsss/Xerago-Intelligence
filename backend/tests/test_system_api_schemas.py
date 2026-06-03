"""Schema tests for system status API."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from xerago_intelligence.api.schemas.system import (
    IntelligenceRunSummary,
    SystemStatusResponse,
)


def test_system_status_response_shape() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    summary = IntelligenceRunSummary(
        run_id="run-1",
        started_at=now,
        completed_at=now,
        sources_polled=19,
        articles_found=120,
        articles_inserted=3,
        articles_filtered=1,
        articles_enriched=2,
        articles_scored=2,
        status="success",
    )
    payload = SystemStatusResponse(
        status="healthy",
        last_run=now,
        next_run=now,
        active_sources=19,
        articles_today=5,
        last_run_summary=summary,
    )
    assert payload.active_sources == 19
    assert payload.last_run_summary is not None
    assert payload.last_run_summary.articles_enriched == 2
