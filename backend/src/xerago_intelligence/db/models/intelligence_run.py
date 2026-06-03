"""SQLAlchemy model for intelligence refresh runs."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from xerago_intelligence.db.base import Base


class IntelligenceRun(Base):
    """One scheduled intelligence refresh cycle."""

    __tablename__ = "intelligence_runs"

    run_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )
    sources_polled: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    articles_found: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    articles_inserted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    articles_filtered: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    articles_enriched: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    articles_scored: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="running")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
