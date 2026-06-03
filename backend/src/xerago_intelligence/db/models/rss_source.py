"""SQLAlchemy models for RSS source registry and ingest health runs."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from xerago_intelligence.db.base import Base


class RssSource(Base):
    """Operational RSS feed registry (Phase 8)."""

    __tablename__ = "rss_sources"

    source_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    rss_url: Mapped[str] = mapped_column(String(2048), nullable=False, unique=True)
    source_tier: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    active_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    failure_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_success_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )
    last_failure_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )
    last_health_status: Mapped[str | None] = mapped_column(String(16), nullable=True)
    last_run_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
    )

    runs: Mapped[list[RssSourceRun]] = relationship(
        "RssSourceRun",
        back_populates="source",
        cascade="all, delete-orphan",
    )


class RssSourceRun(Base):
    """Per-cycle ingest health record for one RSS source."""

    __tablename__ = "rss_source_runs"

    run_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("rss_sources.source_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    http_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    entries_fetched: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    entries_inserted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    entries_skipped_dup: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    entries_skipped_cursor: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    source: Mapped[RssSource] = relationship("RssSource", back_populates="runs")
