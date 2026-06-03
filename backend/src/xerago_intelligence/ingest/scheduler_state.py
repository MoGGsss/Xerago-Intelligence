"""Process-wide scheduler registration for status API."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from xerago_intelligence.ingest.scheduler import IngestionScheduler

_scheduler: IngestionScheduler | None = None
_last_cycle_started_at: datetime | None = None
_last_cycle_completed_at: datetime | None = None
_interval_seconds: int = 15 * 60


def register_scheduler(scheduler: IngestionScheduler) -> None:
    global _scheduler, _interval_seconds
    _scheduler = scheduler
    _interval_seconds = scheduler.interval_seconds


def get_scheduler() -> IngestionScheduler | None:
    return _scheduler


def mark_cycle_started() -> None:
    global _last_cycle_started_at
    _last_cycle_started_at = datetime.now(timezone.utc).replace(tzinfo=None)


def mark_cycle_completed() -> None:
    global _last_cycle_completed_at
    _last_cycle_completed_at = datetime.now(timezone.utc).replace(tzinfo=None)


def get_last_cycle_completed_at() -> datetime | None:
    return _last_cycle_completed_at


def get_next_run_at() -> datetime | None:
    anchor = _last_cycle_started_at or _last_cycle_completed_at
    if anchor is None:
        return datetime.now(timezone.utc).replace(tzinfo=None)
    return anchor + timedelta(seconds=_interval_seconds)
