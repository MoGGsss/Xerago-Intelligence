"""Persistence layer for artifact_department_mappings."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.orm import Session

from xerago_intelligence.db.models.artifact_department_mapping import (
    ArtifactDepartmentMapping,
)
from xerago_intelligence.db.models.artifact_enrichment import ArtifactEnrichment
from xerago_intelligence.taxonomy.department_mapper import (
    DepartmentMappingRecord,
    DepartmentScore,
)


def _to_mapping_record(
    item: DepartmentScore | DepartmentMappingRecord,
) -> DepartmentMappingRecord:
    if isinstance(item, DepartmentMappingRecord):
        return item
    return DepartmentMappingRecord.from_score(item)


class DepartmentMappingRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_artifact_id(self, artifact_id: str) -> list[ArtifactDepartmentMapping]:
        return list(
            self._session.scalars(
                select(ArtifactDepartmentMapping)
                .where(ArtifactDepartmentMapping.artifact_id == artifact_id)
                .order_by(ArtifactDepartmentMapping.department_relevance_score.desc())
            ).all()
        )

    def get_mappings_by_artifact_ids(
        self,
        artifact_ids: list[str],
    ) -> dict[str, list[ArtifactDepartmentMapping]]:
        if not artifact_ids:
            return {}
        rows = self._session.scalars(
            select(ArtifactDepartmentMapping)
            .where(ArtifactDepartmentMapping.artifact_id.in_(artifact_ids))
            .order_by(
                ArtifactDepartmentMapping.artifact_id,
                ArtifactDepartmentMapping.department_relevance_score.desc(),
            )
        ).all()
        grouped: dict[str, list[ArtifactDepartmentMapping]] = {}
        for row in rows:
            grouped.setdefault(row.artifact_id, []).append(row)
        return grouped

    def replace_mappings(
        self,
        artifact_id: str,
        mappings: list[DepartmentScore] | list[DepartmentMappingRecord],
        *,
        mapping_version: str,
        mapped_at: datetime | None = None,
    ) -> list[ArtifactDepartmentMapping]:
        now = mapped_at or datetime.now(timezone.utc).replace(tzinfo=None)
        self._session.execute(
            delete(ArtifactDepartmentMapping).where(
                ArtifactDepartmentMapping.artifact_id == artifact_id
            )
        )
        saved: list[ArtifactDepartmentMapping] = []
        for item in mappings:
            record = _to_mapping_record(item)
            row = ArtifactDepartmentMapping(
                artifact_id=artifact_id,
                department_name=record.department_name,
                department_relevance_score=record.department_relevance_score,
                mapping_version=mapping_version,
                impact_summary=record.impact_summary,
                impact_category=record.impact_category,
                opportunity_type=record.opportunity_type,
                department_opportunity_score=record.department_opportunity_score,
                impact_reason=record.impact_reason,
                impact_version=record.impact_version,
                mapped_at=now,
            )
            self._session.add(row)
            saved.append(row)
        self._session.flush()
        return saved

    def update_impacts(
        self,
        artifact_id: str,
        impacts: list[DepartmentMappingRecord],
    ) -> list[ArtifactDepartmentMapping]:
        """Update impact fields on existing rows matched by department_name."""
        for record in impacts:
            stmt = (
                update(ArtifactDepartmentMapping)
                .where(
                    ArtifactDepartmentMapping.artifact_id == artifact_id,
                    ArtifactDepartmentMapping.department_name == record.department_name,
                )
                .values(
                    impact_summary=record.impact_summary,
                    impact_category=record.impact_category,
                    opportunity_type=record.opportunity_type,
                    department_opportunity_score=record.department_opportunity_score,
                    impact_reason=record.impact_reason,
                    impact_version=record.impact_version,
                )
            )
            self._session.execute(stmt)
        self._session.flush()
        return self.get_by_artifact_id(artifact_id)

    def count_unmapped_enriched(self) -> int:
        stmt = (
            select(func.count(ArtifactEnrichment.artifact_id))
            .select_from(ArtifactEnrichment)
            .outerjoin(
                ArtifactDepartmentMapping,
                ArtifactEnrichment.artifact_id
                == ArtifactDepartmentMapping.artifact_id,
            )
            .where(ArtifactDepartmentMapping.artifact_id.is_(None))
        )
        return int(self._session.scalar(stmt) or 0)

    def count_stale(self, mapping_version: str) -> int:
        latest = (
            select(
                ArtifactDepartmentMapping.artifact_id,
                func.max(ArtifactDepartmentMapping.mapped_at).label("latest_at"),
            )
            .group_by(ArtifactDepartmentMapping.artifact_id)
            .subquery()
        )
        stmt = (
            select(func.count())
            .select_from(ArtifactDepartmentMapping)
            .join(
                latest,
                (ArtifactDepartmentMapping.artifact_id == latest.c.artifact_id)
                & (ArtifactDepartmentMapping.mapped_at == latest.c.latest_at),
            )
            .where(ArtifactDepartmentMapping.mapping_version != mapping_version)
        )
        return int(self._session.scalar(stmt) or 0)

    def count_missing_impact(self) -> int:
        stmt = select(func.count()).select_from(ArtifactDepartmentMapping).where(
            or_(
                ArtifactDepartmentMapping.impact_summary.is_(None),
                ArtifactDepartmentMapping.impact_version.is_(None),
            )
        )
        return int(self._session.scalar(stmt) or 0)

    def count_stale_impact(self, impact_version: str) -> int:
        latest = (
            select(
                ArtifactDepartmentMapping.artifact_id,
                func.max(ArtifactDepartmentMapping.mapped_at).label("latest_at"),
            )
            .group_by(ArtifactDepartmentMapping.artifact_id)
            .subquery()
        )
        stmt = (
            select(func.count())
            .select_from(ArtifactDepartmentMapping)
            .join(
                latest,
                (ArtifactDepartmentMapping.artifact_id == latest.c.artifact_id)
                & (ArtifactDepartmentMapping.mapped_at == latest.c.latest_at),
            )
            .where(
                or_(
                    ArtifactDepartmentMapping.impact_version.is_(None),
                    ArtifactDepartmentMapping.impact_version != impact_version,
                )
            )
        )
        return int(self._session.scalar(stmt) or 0)
