"""SQLAlchemy model for per-source ingest cursors."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from xerago_intelligence.db.base import Base


class IngestCursor(Base):
    """Tracks incremental ingest position per source_id."""

    __tablename__ = "ingest_cursors"

    source_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    cursor_value: Mapped[str] = mapped_column(Text, nullable=False)
    last_entry_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
