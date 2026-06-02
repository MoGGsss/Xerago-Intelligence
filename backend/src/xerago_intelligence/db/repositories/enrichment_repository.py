"""Persistence layer for artifact_enrichments."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from xerago_intelligence.db.models.artifact import Artifact
from xerago_intelligence.db.models.artifact_enrichment import ArtifactEnrichment
from xerago_intelligence.types.enrichment import EnrichmentPayload


class EnrichmentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_artifact_id(self, artifact_id: str) -> ArtifactEnrichment | None:
        return self._session.scalar(
            select(ArtifactEnrichment).where(
                ArtifactEnrichment.artifact_id == artifact_id
            )
        )

    def get_latest(self) -> ArtifactEnrichment | None:
        return self._session.scalar(
            select(ArtifactEnrichment).order_by(
                ArtifactEnrichment.enriched_at.desc()
            ).limit(1)
        )

    def get_latest_with_artifact(self) -> tuple[ArtifactEnrichment, Artifact] | None:
        row = self._session.execute(
            select(ArtifactEnrichment, Artifact)
            .join(Artifact, ArtifactEnrichment.artifact_id == Artifact.artifact_id)
            .order_by(ArtifactEnrichment.enriched_at.desc())
            .limit(1)
        ).first()
        if row is None:
            return None
        return row[0], row[1]

    def update_score(
        self,
        artifact_id: str,
        *,
        strategic_score: int,
        priority_level: str,
        score_reason: str,
        scored_at: datetime | None = None,
    ) -> ArtifactEnrichment | None:
        row = self.get_by_artifact_id(artifact_id)
        if row is None:
            return None
        now = scored_at or datetime.now(timezone.utc).replace(tzinfo=None)
        row.strategic_score = strategic_score
        row.priority_level = priority_level
        row.score_reason = score_reason
        row.scored_at = now
        self._session.flush()
        return row

    def save_enrichment(
        self,
        *,
        artifact_id: str,
        payload: EnrichmentPayload,
        provider: str,
        model: str,
        prompt_version: str,
        raw_response: str | None = None,
        confidence_score: int = 0,
        validation_status: str = "pending",
        classification_reason: str | None = None,
    ) -> ArtifactEnrichment:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        row = self.get_by_artifact_id(artifact_id)
        if row is None:
            row = ArtifactEnrichment(
                artifact_id=artifact_id,
                summary=payload.summary.strip(),
                why_it_matters=payload.why_it_matters.strip(),
                domain=payload.domain.strip(),
                signal_type=payload.signal_type.strip(),
                provider=provider,
                model=model,
                prompt_version=prompt_version,
                raw_response=raw_response,
                confidence_score=confidence_score,
                validation_status=validation_status,
                classification_reason=classification_reason,
                enriched_at=now,
            )
            self._session.add(row)
        else:
            row.summary = payload.summary.strip()
            row.why_it_matters = payload.why_it_matters.strip()
            row.domain = payload.domain.strip()
            row.signal_type = payload.signal_type.strip()
            row.provider = provider
            row.model = model
            row.prompt_version = prompt_version
            row.raw_response = raw_response
            row.confidence_score = confidence_score
            row.validation_status = validation_status
            row.classification_reason = classification_reason
            row.enriched_at = now
        self._session.flush()
        return row

    def update_classification(
        self,
        artifact_id: str,
        *,
        confidence_score: int,
        validation_status: str,
        classification_reason: str,
    ) -> ArtifactEnrichment | None:
        row = self.get_by_artifact_id(artifact_id)
        if row is None:
            return None
        row.confidence_score = confidence_score
        row.validation_status = validation_status
        row.classification_reason = classification_reason
        self._session.flush()
        return row
