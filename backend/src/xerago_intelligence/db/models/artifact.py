"""SQLAlchemy model for ingested RSS artifacts."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from xerago_intelligence.db.base import Base


class Artifact(Base):
    """
    Raw ingested article from an RSS feed.

    Duplicate prevention: unique constraint on ``url``.
    """

    __tablename__ = "artifacts"

    artifact_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    source_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False, unique=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    raw_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )

    def __repr__(self) -> str:
        return f"<Artifact {self.artifact_id!s} source={self.source_id!r} url={self.url!r}>"
