"""Persistence layer for artifacts."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from xerago_intelligence.db.models.artifact import Artifact
from xerago_intelligence.utils.url import normalize_url


class ArtifactRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, artifact_id: str) -> Artifact | None:
        return self._session.get(Artifact, artifact_id)

    def get_by_url(self, url: str) -> Artifact | None:
        normalized = normalize_url(url)
        return self._session.scalar(
            select(Artifact).where(Artifact.url == normalized)
        )

    def insert_article(
        self,
        *,
        source_id: str,
        title: str,
        url: str,
        published_at: datetime,
        raw_content: str | None,
        ingested_at: datetime | None = None,
    ) -> tuple[Artifact | None, bool]:
        """
        Insert a new artifact if the URL is not already stored.

        Returns (artifact, created). On duplicate URL, returns (None, False).
        """
        normalized_url = normalize_url(url)
        if self.get_by_url(normalized_url) is not None:
            return None, False

        artifact = Artifact(
            source_id=source_id,
            title=title.strip(),
            url=normalized_url,
            published_at=published_at,
            raw_content=raw_content,
            ingested_at=ingested_at or datetime.now(timezone.utc).replace(tzinfo=None),
        )
        self._session.add(artifact)
        try:
            self._session.flush()
        except IntegrityError:
            self._session.expunge(artifact)
            return None, False
        return artifact, True

    def count_all(self) -> int:
        return int(self._session.scalar(select(func.count()).select_from(Artifact)) or 0)

    def count_by_source(self, source_id: str) -> int:
        return int(
            self._session.scalar(
                select(func.count())
                .select_from(Artifact)
                .where(Artifact.source_id == source_id)
            )
            or 0
        )

    def list_recent(self, *, limit: int = 10, source_id: str | None = None) -> list[Artifact]:
        stmt = select(Artifact).order_by(Artifact.ingested_at.desc()).limit(limit)
        if source_id is not None:
            stmt = stmt.where(Artifact.source_id == source_id)
        return list(self._session.scalars(stmt).all())

    def list_ingested_since(
        self,
        *,
        source_id: str,
        ingested_since: datetime,
    ) -> list[Artifact]:
        stmt = (
            select(Artifact)
            .where(Artifact.source_id == source_id)
            .where(Artifact.ingested_at >= ingested_since)
            .order_by(Artifact.ingested_at.asc())
        )
        return list(self._session.scalars(stmt).all())
