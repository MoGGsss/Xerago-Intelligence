"""Persistence for intelligence refresh runs."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from xerago_intelligence.db.models.intelligence_run import IntelligenceRun


@dataclass
class IntelligenceRunMetrics:
    sources_polled: int = 0
    articles_found: int = 0
    articles_inserted: int = 0
    articles_filtered: int = 0
    articles_enriched: int = 0
    articles_scored: int = 0


class IntelligenceRunRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def start_run(self) -> IntelligenceRun:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        row = IntelligenceRun(
            run_id=str(uuid.uuid4()),
            started_at=now,
            status="running",
        )
        self._session.add(row)
        self._session.flush()
        return row

    def complete_run(
        self,
        run_id: str,
        *,
        metrics: IntelligenceRunMetrics,
        status: str,
        error_message: str | None = None,
    ) -> IntelligenceRun | None:
        row = self._session.get(IntelligenceRun, run_id)
        if row is None:
            return None
        row.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
        row.sources_polled = metrics.sources_polled
        row.articles_found = metrics.articles_found
        row.articles_inserted = metrics.articles_inserted
        row.articles_filtered = metrics.articles_filtered
        row.articles_enriched = metrics.articles_enriched
        row.articles_scored = metrics.articles_scored
        row.status = status
        row.error_message = error_message[:4000] if error_message else None
        self._session.flush()
        return row

    def get_latest(self) -> IntelligenceRun | None:
        stmt = (
            select(IntelligenceRun)
            .order_by(IntelligenceRun.started_at.desc())
            .limit(1)
        )
        return self._session.scalar(stmt)

    def get_latest_completed(self) -> IntelligenceRun | None:
        """Most recent finished cycle (success, partial, or failure)."""
        stmt = (
            select(IntelligenceRun)
            .where(IntelligenceRun.completed_at.is_not(None))
            .order_by(IntelligenceRun.completed_at.desc())
            .limit(1)
        )
        return self._session.scalar(stmt)

    def get_by_id(self, run_id: str) -> IntelligenceRun | None:
        return self._session.get(IntelligenceRun, run_id)
