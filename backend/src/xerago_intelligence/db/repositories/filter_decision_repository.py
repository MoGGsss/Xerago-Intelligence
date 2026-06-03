"""Persistence layer for artifact_filter_decisions."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from xerago_intelligence.db.models.artifact_filter_decision import ArtifactFilterDecision
from xerago_intelligence.filtering.negative_scorer import NegativeFilterResult


class FilterDecisionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_latest(self, artifact_id: str) -> ArtifactFilterDecision | None:
        return self._session.scalar(
            select(ArtifactFilterDecision)
            .where(ArtifactFilterDecision.artifact_id == artifact_id)
            .order_by(ArtifactFilterDecision.evaluated_at.desc())
            .limit(1)
        )

    def is_skipped(self, artifact_id: str, filter_version: str) -> bool:
        row = self._session.scalar(
            select(ArtifactFilterDecision)
            .where(ArtifactFilterDecision.artifact_id == artifact_id)
            .where(ArtifactFilterDecision.filter_version == filter_version)
            .limit(1)
        )
        return row is not None and row.decision == "skipped"

    def save_decision(
        self,
        artifact_id: str,
        result: NegativeFilterResult,
        *,
        evaluated_at: datetime | None = None,
    ) -> ArtifactFilterDecision:
        now = evaluated_at or datetime.now(timezone.utc).replace(tzinfo=None)
        self._session.execute(
            delete(ArtifactFilterDecision).where(
                ArtifactFilterDecision.artifact_id == artifact_id,
                ArtifactFilterDecision.filter_version == result.filter_version,
            )
        )
        row = ArtifactFilterDecision(
            artifact_id=artifact_id,
            filter_version=result.filter_version,
            negative_score=result.negative_score,
            skip_threshold=result.skip_threshold,
            decision="skipped" if result.should_skip else "passed",
            skip_reason=result.skip_reason,
            matched_keywords=list(result.matched_keywords),
            evaluated_at=now,
        )
        self._session.add(row)
        self._session.flush()
        return row

    def count_by_decision(self, decision: str, filter_version: str) -> int:
        return int(
            self._session.scalar(
                select(func.count(ArtifactFilterDecision.decision_id))
                .where(ArtifactFilterDecision.decision == decision)
                .where(ArtifactFilterDecision.filter_version == filter_version)
            )
            or 0
        )

    @staticmethod
    def to_result(row: ArtifactFilterDecision) -> NegativeFilterResult:
        matched = row.matched_keywords
        if isinstance(matched, str):
            matched = json.loads(matched)
        return NegativeFilterResult(
            negative_score=row.negative_score,
            skip_threshold=row.skip_threshold,
            should_skip=row.decision == "skipped",
            skip_reason=row.skip_reason,
            matched_keywords=tuple(matched),
            filter_version=row.filter_version,
        )
