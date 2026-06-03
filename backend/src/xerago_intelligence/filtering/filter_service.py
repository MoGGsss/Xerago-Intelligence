"""Negative filter orchestration with persistence."""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from xerago_intelligence.config import get_settings
from xerago_intelligence.db.repositories.artifact_repository import ArtifactRepository
from xerago_intelligence.db.repositories.filter_decision_repository import (
    FilterDecisionRepository,
)
from xerago_intelligence.filtering.negative_filter import NegativeFilter
from xerago_intelligence.filtering.negative_keywords import NEGATIVE_FILTER_VERSION
from xerago_intelligence.filtering.negative_scorer import NegativeFilterResult, NegativeScorer

logger = logging.getLogger(__name__)


class NegativeFilterService:
    """Evaluate and persist negative filter decisions before enrichment."""

    def __init__(
        self,
        session: Session,
        *,
        negative_filter: NegativeFilter | None = None,
    ) -> None:
        settings = get_settings()
        self._enabled = settings.negative_filter_enabled
        threshold = settings.negative_score_skip_threshold
        scorer = NegativeScorer(skip_threshold=threshold)
        self._filter = negative_filter or NegativeFilter(scorer=scorer)
        self._artifacts = ArtifactRepository(session)
        self._decisions = FilterDecisionRepository(session)

    def evaluate_and_persist(
        self,
        artifact_id: str,
        *,
        force: bool = False,
    ) -> NegativeFilterResult:
        if not self._enabled:
            return self._passed_result(threshold=get_settings().negative_score_skip_threshold)

        if not force:
            cached = self._decisions.get_latest(artifact_id)
            if cached is not None and cached.filter_version == NEGATIVE_FILTER_VERSION:
                return self._decisions.to_result(cached)

        artifact = self._artifacts.get_by_id(artifact_id)
        if artifact is None:
            raise ValueError(f"Artifact not found: {artifact_id}")

        result = self._filter.evaluate(
            title=artifact.title,
            raw_content=artifact.raw_content,
        )
        self._decisions.save_decision(artifact_id, result)
        logger.info(
            "Negative filter artifact_id=%s score=%s decision=%s matched=%s",
            artifact_id,
            result.negative_score,
            "skipped" if result.should_skip else "passed",
            list(result.matched_keywords),
        )
        return result

    def is_skipped(self, artifact_id: str) -> bool:
        if not self._enabled:
            return False
        return self._decisions.is_skipped(artifact_id, NEGATIVE_FILTER_VERSION)

    @staticmethod
    def _passed_result(*, threshold: int) -> NegativeFilterResult:
        return NegativeFilterResult(
            negative_score=0,
            skip_threshold=threshold,
            should_skip=False,
            skip_reason=None,
            matched_keywords=(),
        )
