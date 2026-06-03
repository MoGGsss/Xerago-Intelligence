"""SQLAlchemy model for artifact department mappings."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from xerago_intelligence.db.base import Base


class ArtifactDepartmentMapping(Base):
    """Department relevance and impact fields for one artifact (many rows per artifact)."""

    __tablename__ = "artifact_department_mappings"

    mapping_id: Mapped[str] = mapped_column(
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
    department_name: Mapped[str] = mapped_column(String(64), nullable=False)
    department_relevance_score: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )
    mapping_version: Mapped[str] = mapped_column(String(32), nullable=False)
    impact_summary: Mapped[str | None] = mapped_column(String(256), nullable=True)
    impact_category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    opportunity_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    department_opportunity_score: Mapped[int | None] = mapped_column(
        SmallInteger,
        nullable=True,
    )
    impact_reason: Mapped[str | None] = mapped_column(String(512), nullable=True)
    impact_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    mapped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
    )
