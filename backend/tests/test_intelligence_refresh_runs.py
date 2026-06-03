"""Tests that scheduler cycles persist intelligence_runs rows."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from xerago_intelligence.db import session_scope
from xerago_intelligence.db.connection import probe_connection
from xerago_intelligence.db.repositories.intelligence_run_repository import (
    IntelligenceRunMetrics,
    IntelligenceRunRepository,
)
from xerago_intelligence.ingest.intelligence_refresh import (
    IntelligenceRefreshService,
    SourceCycleResult,
)


def test_run_cycle_persists_completed_intelligence_run() -> None:
    if not probe_connection().ok:
        return

    with session_scope() as session:
        service = IntelligenceRefreshService(session)
        with patch.object(service._sources, "list_active", return_value=[]):
            cycle = service.run_cycle()

    assert cycle.fatal_error is None
    assert cycle.status == "success"

    with session_scope() as session:
        latest = IntelligenceRunRepository(session).get_latest_completed()
        assert latest is not None
        assert latest.completed_at is not None
        assert latest.status == "success"
        assert latest.run_id


def test_fatal_cycle_still_persists_failure_run() -> None:
    if not probe_connection().ok:
        return

    fake_source = MagicMock(source_id="test-source", rss_url="https://example.com/feed")

    with session_scope() as session:
        service = IntelligenceRefreshService(session)
        with (
            patch.object(service._sources, "list_active", return_value=[fake_source]),
            patch.object(
                service,
                "_process_source",
                side_effect=RuntimeError("simulated cycle fault"),
            ),
        ):
            cycle = service.run_cycle()

    assert cycle.fatal_error == "simulated cycle fault"

    with session_scope() as session:
        latest = IntelligenceRunRepository(session).get_latest_completed()
        assert latest is not None
        assert latest.status == "failure"
        assert latest.error_message == "simulated cycle fault"


def test_run_status_transitions_running_to_success() -> None:
    if not probe_connection().ok:
        return

    with session_scope() as session:
        runs = IntelligenceRunRepository(session)
        row = runs.start_run()
        assert row.status == "running"
        assert row.completed_at is None
        runs.complete_run(
            row.run_id,
            metrics=IntelligenceRunMetrics(),
            status="success",
        )
        finished = runs.get_by_id(row.run_id)
        assert finished is not None
        assert finished.status == "success"
        assert finished.completed_at is not None


def test_partial_cycle_persisted_when_source_fails() -> None:
    if not probe_connection().ok:
        return

    fake_source = MagicMock(source_id="test-source", rss_url="https://example.com/feed")
    failed = SourceCycleResult(source_id="test-source", failed=True)

    with session_scope() as session:
        service = IntelligenceRefreshService(session)
        with (
            patch.object(service._sources, "list_active", return_value=[fake_source]),
            patch.object(service, "_process_source", return_value=failed),
        ):
            cycle = service.run_cycle()

    assert cycle.fatal_error is None
    assert cycle.status == "partial"

    with session_scope() as session:
        latest = IntelligenceRunRepository(session).get_latest_completed()
        assert latest is not None
        assert latest.status == "partial"
