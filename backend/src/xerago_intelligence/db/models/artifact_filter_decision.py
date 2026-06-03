"""SQLAlchemy model for artifact filter decisions."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from xerago_intelligence.db.base import Base


class ArtifactFilterDecision(Base):
    """Persisted negative filter evaluation for one artifact."""

    __tablename__ = "artifact_filter_decisions"

    decision_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    artifact_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("artifacts.artifact_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    filter_version: Mapped[str] = mapped_column(String(32), nullable=False)
    negative_score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    skip_threshold: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    decision: Mapped[str] = mapped_column(String(16), nullable=False)
    skip_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    matched_keywords: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
    )
