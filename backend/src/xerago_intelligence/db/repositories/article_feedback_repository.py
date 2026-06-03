"""Persistence layer for article_feedback."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from xerago_intelligence.db.models.article_feedback import ArticleFeedback


class DuplicateArticleFeedbackError(Exception):
    """Raised when feedback already exists for artifact + department."""


class ArticleFeedbackRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def exists(self, artifact_id: str, department_name: str) -> bool:
        row = self._session.scalar(
            select(ArticleFeedback.feedback_id)
            .where(ArticleFeedback.artifact_id == artifact_id)
            .where(ArticleFeedback.department_name == department_name)
            .limit(1)
        )
        return row is not None

    def create(
        self,
        *,
        artifact_id: str,
        department_name: str,
        feedback_type: str,
        feedback_reason: str | None,
        created_at: datetime | None = None,
    ) -> ArticleFeedback:
        if self.exists(artifact_id, department_name):
            raise DuplicateArticleFeedbackError(
                f"Feedback already recorded for {artifact_id} / {department_name}"
            )

        now = created_at or datetime.now(timezone.utc).replace(tzinfo=None)
        row = ArticleFeedback(
            artifact_id=artifact_id,
            department_name=department_name,
            feedback_type=feedback_type,
            feedback_reason=feedback_reason,
            created_at=now,
        )
        self._session.add(row)
        try:
            self._session.flush()
        except IntegrityError as exc:
            self._session.rollback()
            raise DuplicateArticleFeedbackError(
                f"Feedback already recorded for {artifact_id} / {department_name}"
            ) from exc
        return row
