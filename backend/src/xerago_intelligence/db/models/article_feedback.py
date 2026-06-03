"""SQLAlchemy model for article feedback."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from xerago_intelligence.db.base import Base


class ArticleFeedback(Base):
    """One feedback record per artifact and department."""

    __tablename__ = "article_feedback"

    feedback_id: Mapped[str] = mapped_column(
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
    department_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    feedback_type: Mapped[str] = mapped_column(String(16), nullable=False)
    feedback_reason: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
    )
