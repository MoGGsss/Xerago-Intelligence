"""Read queries for intelligence API (artifacts + enrichments)."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from xerago_intelligence.db.models.artifact import Artifact
from xerago_intelligence.db.models.artifact_enrichment import ArtifactEnrichment
from xerago_intelligence.taxonomy import department_for_domain
from xerago_intelligence.types.intelligence import IntelligencePage, IntelligenceRecord


@dataclass(frozen=True)
class IntelligenceListFilters:
    page: int = 1
    page_size: int = 20
    domain: str | None = None
    priority: str | None = None
    query: str | None = None


class IntelligenceQueryRepository:
    """Join artifacts with enrichments for read-only intelligence feed."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_artifact_id(self, artifact_id: str) -> IntelligenceRecord | None:
        stmt = self._base_select().where(Artifact.artifact_id == artifact_id)
        row = self._session.execute(stmt).first()
        if row is None:
            return None
        return self._to_record(row[0], row[1])

    def list_intelligence(
        self,
        filters: IntelligenceListFilters,
    ) -> IntelligencePage:
        page = max(1, filters.page)
        page_size = max(1, min(filters.page_size, 100))
        offset = (page - 1) * page_size

        count_stmt = select(func.count(Artifact.artifact_id)).select_from(Artifact).join(
            ArtifactEnrichment,
            Artifact.artifact_id == ArtifactEnrichment.artifact_id,
        )
        if filters.domain:
            count_stmt = count_stmt.where(
                ArtifactEnrichment.domain == filters.domain.strip().lower()
            )
        if filters.priority:
            count_stmt = count_stmt.where(
                func.upper(ArtifactEnrichment.priority_level)
                == filters.priority.strip().upper()
            )
        if filters.query:
            count_stmt = count_stmt.where(self._search_predicate(filters.query))
        total = int(self._session.scalar(count_stmt) or 0)

        base = self._filtered_select(filters.domain, filters.priority, filters.query)

        stmt = (
            base.order_by(
                func.coalesce(ArtifactEnrichment.strategic_score, -1).desc(),
                Artifact.published_at.desc(),
            )
            .offset(offset)
            .limit(page_size)
        )
        rows = self._session.execute(stmt).all()
        items = [self._to_record(artifact, enrichment) for artifact, enrichment in rows]

        return IntelligencePage(
            items=items,
            page=page,
            page_size=page_size,
            total=total,
        )

    def list_top(self, *, limit: int = 10) -> list[IntelligenceRecord]:
        limit = max(1, min(limit, 50))
        stmt = (
            self._base_select()
            .where(ArtifactEnrichment.strategic_score.is_not(None))
            .order_by(
                ArtifactEnrichment.strategic_score.desc(),
                Artifact.published_at.desc(),
            )
            .limit(limit)
        )
        rows = self._session.execute(stmt).all()
        return [self._to_record(artifact, enrichment) for artifact, enrichment in rows]

    def _base_select(self) -> Select:
        return select(Artifact, ArtifactEnrichment).join(
            ArtifactEnrichment,
            Artifact.artifact_id == ArtifactEnrichment.artifact_id,
        )

    def _filtered_select(
        self,
        domain: str | None,
        priority: str | None,
        query: str | None,
    ) -> Select:
        stmt = self._base_select()
        if domain:
            stmt = stmt.where(ArtifactEnrichment.domain == domain.strip().lower())
        if priority:
            stmt = stmt.where(
                func.upper(ArtifactEnrichment.priority_level) == priority.strip().upper()
            )
        if query:
            stmt = stmt.where(self._search_predicate(query))
        return stmt

    @staticmethod
    def _search_predicate(query: str):
        normalized = query.strip().lower()
        return (
            func.lower(Artifact.title).like(f"%{normalized}%")
            | func.lower(Artifact.url).like(f"%{normalized}%")
            | func.lower(ArtifactEnrichment.summary).like(f"%{normalized}%")
            | func.lower(ArtifactEnrichment.why_it_matters).like(f"%{normalized}%")
            | func.lower(ArtifactEnrichment.domain).like(f"%{normalized}%")
            | func.lower(ArtifactEnrichment.signal_type).like(f"%{normalized}%")
        )

    @staticmethod
    def _to_record(
        artifact: Artifact,
        enrichment: ArtifactEnrichment,
    ) -> IntelligenceRecord:
        return IntelligenceRecord(
            artifact_id=artifact.artifact_id,
            title=artifact.title,
            url=artifact.url,
            published_at=artifact.published_at,
            summary=enrichment.summary,
            why_it_matters=enrichment.why_it_matters,
            domain=enrichment.domain,
            signal_type=enrichment.signal_type,
            confidence_score=enrichment.confidence_score,
            validation_status=enrichment.validation_status,
            strategic_score=enrichment.strategic_score,
            priority_level=enrichment.priority_level,
            department=department_for_domain(enrichment.domain),
        )
