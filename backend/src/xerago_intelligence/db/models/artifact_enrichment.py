"""SQLAlchemy model for artifact LLM enrichments."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from xerago_intelligence.db.base import Base


class ArtifactEnrichment(Base):
    """LLM-generated summary and classification for one artifact."""

    __tablename__ = "artifact_enrichments"

    enrichment_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    artifact_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("artifacts.artifact_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    why_it_matters: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    signal_type: Mapped[str] = mapped_column(String(128), nullable=False)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(32), nullable=False)
    raw_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=0,
    )
    validation_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="pending",
    )
    classification_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    strategic_score: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    priority_level: Mapped[str | None] = mapped_column(String(16), nullable=True)
    score_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    scored_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )
    enriched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
