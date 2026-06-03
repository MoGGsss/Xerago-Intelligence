"""Artifact enrichment orchestration."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlalchemy.orm import Session

from xerago_intelligence.ai.client import AIClient, GenerateResult, create_ai_client
from xerago_intelligence.classification.confidence import (
    build_classification_reason,
    calculate_confidence,
    validation_status_for_confidence,
)
from xerago_intelligence.classification.validator import ClassificationValidator
from xerago_intelligence.db.models.artifact import Artifact
from xerago_intelligence.db.models.artifact_enrichment import ArtifactEnrichment
from xerago_intelligence.db.repositories.artifact_repository import ArtifactRepository
from xerago_intelligence.db.repositories.enrichment_repository import EnrichmentRepository
from xerago_intelligence.enrichment.parse import EnrichmentParseError, parse_enrichment_json
from xerago_intelligence.enrichment.prompts import PROMPT_VERSION, build_enrichment_prompt
from xerago_intelligence.filtering import EnrichmentSkippedError, NegativeFilterService
from xerago_intelligence.mapping.department_service import DepartmentMappingService
from xerago_intelligence.scoring import ScoreInput, StrategicScorer
from xerago_intelligence.types.enrichment import EnrichmentPayload

logger = logging.getLogger(__name__)


def log_raw_model_response(text: str) -> None:
    """Diagnostic logging immediately before JSON parse."""
    logger.info("Enrichment raw response length=%d", len(text))
    logger.info(
        "Enrichment raw response (first 1000 chars): %s",
        text[:1000],
    )
    logger.info("Enrichment raw response full text: %s", text)


@dataclass(frozen=True)
class ClassificationOutcome:
    confidence_score: int
    validation_status: str
    classification_reason: str


@dataclass(frozen=True)
class EnrichmentServiceResult:
    artifact_id: str
    payload: EnrichmentPayload
    row: ArtifactEnrichment
    created: bool
    confidence_score: int
    validation_status: str
    classification_reason: str


class ArtifactEnrichmentService:
    """Generate and persist LLM enrichment for a stored artifact."""

    def __init__(
        self,
        session: Session,
        *,
        ai_client: AIClient | None = None,
        validator: ClassificationValidator | None = None,
    ) -> None:
        self._session = session
        self._artifacts = ArtifactRepository(session)
        self._enrichments = EnrichmentRepository(session)
        self._ai = ai_client or create_ai_client()
        self._validator = validator or ClassificationValidator()
        self._scorer = StrategicScorer()
        self._department_mapper = DepartmentMappingService(session)
        self._negative_filter = NegativeFilterService(session)

    def classify(
        self,
        domain: str,
        signal_type: str,
    ) -> ClassificationOutcome:
        """Validate classifications and compute confidence."""
        validation = self._validator.validate(domain, signal_type)
        confidence_score = calculate_confidence(validation)
        validation_status = validation_status_for_confidence(confidence_score)
        classification_reason = build_classification_reason(validation)
        return ClassificationOutcome(
            confidence_score=confidence_score,
            validation_status=validation_status,
            classification_reason=classification_reason,
        )

    def validate_and_update(self, artifact_id: str) -> ArtifactEnrichment | None:
        """Re-validate stored enrichment classifications and persist scores."""
        row = self._enrichments.get_by_artifact_id(artifact_id)
        if row is None:
            return None
        outcome = self.classify(row.domain, row.signal_type)
        return self._enrichments.update_classification(
            artifact_id,
            confidence_score=outcome.confidence_score,
            validation_status=outcome.validation_status,
            classification_reason=outcome.classification_reason,
        )

    def enrich_artifact(
        self,
        artifact_id: str,
        *,
        force: bool = False,
        precomputed_response: str | None = None,
    ) -> EnrichmentServiceResult:
        artifact = self._artifacts.get_by_id(artifact_id)
        if artifact is None:
            raise ValueError(f"Artifact not found: {artifact_id}")

        existing = self._enrichments.get_by_artifact_id(artifact_id)
        if existing is not None and not force:
            outcome = self.classify(existing.domain, existing.signal_type)
            if existing.validation_status == "pending":
                self._enrichments.update_classification(
                    artifact_id,
                    confidence_score=outcome.confidence_score,
                    validation_status=outcome.validation_status,
                    classification_reason=outcome.classification_reason,
                )
                existing = self._enrichments.get_by_artifact_id(artifact_id)
            assert existing is not None
            self._department_mapper.map_artifact(artifact_id, force=False)
            return EnrichmentServiceResult(
                artifact_id=artifact_id,
                payload=EnrichmentPayload(
                    summary=existing.summary,
                    why_it_matters=existing.why_it_matters,
                    domain=existing.domain,
                    signal_type=existing.signal_type,
                ),
                row=existing,
                created=False,
                confidence_score=existing.confidence_score,
                validation_status=existing.validation_status,
                classification_reason=existing.classification_reason or "",
            )

        filter_result = self._negative_filter.evaluate_and_persist(
            artifact_id,
            force=force,
        )
        if filter_result.should_skip:
            raise EnrichmentSkippedError(artifact_id, filter_result)

        prompt = build_enrichment_prompt(
            title=artifact.title,
            source_id=artifact.source_id,
            url=artifact.url,
            published_at=artifact.published_at.isoformat(),
            body=artifact.raw_content,
        )

        if precomputed_response is not None:
            generate_result = GenerateResult(
                text=precomputed_response,
                model=self._ai.model_name,
                provider=self._ai.provider_name,
            )
        else:
            generate_result = self._ai.generate(prompt, json_mode=False)

        log_raw_model_response(generate_result.text)
        try:
            payload = parse_enrichment_json(generate_result.text)
        except EnrichmentParseError:
            logger.exception(
                "Failed to parse enrichment JSON for artifact_id=%s",
                artifact_id,
            )
            raise

        outcome = self.classify(payload.domain, payload.signal_type)

        created = existing is None
        row = self._enrichments.save_enrichment(
            artifact_id=artifact_id,
            payload=payload,
            provider=generate_result.provider,
            model=generate_result.model,
            prompt_version=PROMPT_VERSION,
            raw_response=generate_result.text,
            confidence_score=outcome.confidence_score,
            validation_status=outcome.validation_status,
            classification_reason=outcome.classification_reason,
        )
        score_result = self._scorer.score(
            ScoreInput(
                confidence_score=outcome.confidence_score,
                domain=payload.domain,
                signal_type=payload.signal_type,
                published_at=artifact.published_at,
            )
        )
        scored_row = self._enrichments.update_score(
            artifact_id,
            strategic_score=score_result.strategic_score,
            priority_level=score_result.priority_level,
            score_reason=score_result.score_reason,
        )
        if scored_row is not None:
            row = scored_row

        logger.info(
            "Enriched artifact_id=%s domain=%s signal_type=%s "
            "confidence=%s status=%s score=%s priority=%s",
            artifact_id,
            payload.domain,
            payload.signal_type,
            outcome.confidence_score,
            outcome.validation_status,
            score_result.strategic_score,
            score_result.priority_level,
        )

        self._department_mapper.map_artifact(artifact_id, force=True)

        return EnrichmentServiceResult(
            artifact_id=artifact_id,
            payload=payload,
            row=row,
            created=created,
            confidence_score=outcome.confidence_score,
            validation_status=outcome.validation_status,
            classification_reason=outcome.classification_reason,
        )

    def get_artifact(self, artifact_id: str) -> Artifact | None:
        return self._artifacts.get_by_id(artifact_id)
