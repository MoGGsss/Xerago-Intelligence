"""Persistence for RSS source registry and ingest health."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from xerago_intelligence.db.models.rss_source import RssSource, RssSourceRun
from xerago_intelligence.ingest.source_catalog import PHASE_8_RSS_SOURCES, RssSourceSeed


class RssSourceRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def count_all(self) -> int:
        return int(
            self._session.scalar(select(func.count()).select_from(RssSource)) or 0
        )

    def get_by_id(self, source_id: str) -> RssSource | None:
        return self._session.get(RssSource, source_id)

    def list_active(self) -> list[RssSource]:
        stmt = (
            select(RssSource)
            .where(RssSource.active_flag.is_(True))
            .order_by(RssSource.source_tier.asc(), RssSource.source_id.asc())
        )
        return list(self._session.scalars(stmt).all())

    def list_all(self) -> list[RssSource]:
        stmt = select(RssSource).order_by(
            RssSource.source_tier.asc(),
            RssSource.source_id.asc(),
        )
        return list(self._session.scalars(stmt).all())

    def upsert_seed(self, seed: RssSourceSeed) -> RssSource:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        existing = self.get_by_id(seed.source_id)
        if existing is None:
            row = RssSource(
                source_id=seed.source_id,
                source_name=seed.source_name,
                source_url=seed.source_url,
                rss_url=seed.rss_url,
                source_tier=seed.source_tier,
                active_flag=seed.active_flag,
                failure_count=0,
                created_at=now,
                updated_at=now,
            )
            self._session.add(row)
            self._session.flush()
            return row

        existing.source_name = seed.source_name
        existing.source_url = seed.source_url
        existing.rss_url = seed.rss_url
        existing.source_tier = seed.source_tier
        existing.active_flag = seed.active_flag
        existing.updated_at = now
        self._session.flush()
        return existing

    def seed_phase8_catalog(self) -> int:
        """Upsert all Phase 8 catalog entries; returns count touched."""
        for seed in PHASE_8_RSS_SOURCES:
            self.upsert_seed(seed)
        return len(PHASE_8_RSS_SOURCES)

    def record_run_start(self, source_id: str) -> str:
        run_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        source = self.get_by_id(source_id)
        if source is not None:
            source.last_run_at = now
        return run_id

    def record_run_success(
        self,
        *,
        run_id: str,
        source_id: str,
        started_at: datetime,
        http_status: int | None,
        entries_fetched: int,
        entries_inserted: int,
        entries_skipped_dup: int,
        entries_skipped_cursor: int,
    ) -> None:
        finished_at = datetime.now(timezone.utc).replace(tzinfo=None)
        self._session.add(
            RssSourceRun(
                run_id=run_id,
                source_id=source_id,
                started_at=started_at,
                finished_at=finished_at,
                status="success",
                http_status=http_status,
                entries_fetched=entries_fetched,
                entries_inserted=entries_inserted,
                entries_skipped_dup=entries_skipped_dup,
                entries_skipped_cursor=entries_skipped_cursor,
            )
        )
        source = self.get_by_id(source_id)
        if source is not None:
            source.failure_count = 0
            source.last_success_at = finished_at
            source.last_health_status = "healthy"
            source.last_run_at = finished_at
        self._session.flush()

    def record_run_failure(
        self,
        *,
        run_id: str,
        source_id: str,
        started_at: datetime,
        error_message: str,
        http_status: int | None = None,
        entries_fetched: int = 0,
        entries_inserted: int = 0,
        entries_skipped_dup: int = 0,
        entries_skipped_cursor: int = 0,
    ) -> None:
        finished_at = datetime.now(timezone.utc).replace(tzinfo=None)
        self._session.add(
            RssSourceRun(
                run_id=run_id,
                source_id=source_id,
                started_at=started_at,
                finished_at=finished_at,
                status="failure",
                http_status=http_status,
                entries_fetched=entries_fetched,
                entries_inserted=entries_inserted,
                entries_skipped_dup=entries_skipped_dup,
                entries_skipped_cursor=entries_skipped_cursor,
                error_message=error_message[:4000],
            )
        )
        source = self.get_by_id(source_id)
        if source is not None:
            source.failure_count += 1
            source.last_failure_at = finished_at
            source.last_health_status = (
                "degraded" if source.failure_count < 3 else "unhealthy"
            )
            source.last_run_at = finished_at
        self._session.flush()

    def list_recent_runs(
        self,
        *,
        source_id: str | None = None,
        limit: int = 50,
    ) -> list[RssSourceRun]:
        stmt = select(RssSourceRun).order_by(RssSourceRun.started_at.desc()).limit(limit)
        if source_id is not None:
            stmt = stmt.where(RssSourceRun.source_id == source_id)
        return list(self._session.scalars(stmt).all())

    def artifact_counts_by_source(self) -> dict[str, int]:
        from xerago_intelligence.db.models.artifact import Artifact

        rows = self._session.execute(
            select(Artifact.source_id, func.count())
            .group_by(Artifact.source_id)
        ).all()
        return {str(source_id): int(count) for source_id, count in rows}

    def inserted_last_24h_by_source(self) -> dict[str, int]:
        from xerago_intelligence.db.models.artifact import Artifact

        since = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=24)
        rows = self._session.execute(
            select(Artifact.source_id, func.count())
            .where(Artifact.ingested_at >= since)
            .group_by(Artifact.source_id)
        ).all()
        return {str(source_id): int(count) for source_id, count in rows}
