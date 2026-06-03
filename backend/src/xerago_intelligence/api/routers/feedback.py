"""Article feedback API routes."""

from __future__ import annotations

import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from xerago_intelligence.api.dependencies import get_db
from xerago_intelligence.api.schemas.feedback import (
    FeedbackCreateRequest,
    FeedbackCreateResponse,
)
from xerago_intelligence.db.models.artifact import Artifact
from xerago_intelligence.db.repositories.article_feedback_repository import (
    ArticleFeedbackRepository,
    DuplicateArticleFeedbackError,
)
from xerago_intelligence.taxonomy.departments import is_valid_department

router = APIRouter(prefix="/feedback", tags=["feedback"])

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def _artifact_exists(session: Session, artifact_id: str) -> bool:
    return (
        session.scalar(select(Artifact.artifact_id).where(Artifact.artifact_id == artifact_id).limit(1))
        is not None
    )


@router.post(
    "",
    response_model=FeedbackCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_feedback(
    body: FeedbackCreateRequest,
    db: Session = Depends(get_db),
) -> FeedbackCreateResponse:
    artifact_id = body.artifact_id.strip()
    department_name = body.department_name.strip()

    if not _UUID_RE.match(artifact_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="artifact_id must be a UUID",
        )

    if not is_valid_department(department_name):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="department_name is not a recognized department",
        )

    if not _artifact_exists(db, artifact_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="artifact not found",
        )

    repo = ArticleFeedbackRepository(db)
    try:
        row = repo.create(
            artifact_id=artifact_id,
            department_name=department_name,
            feedback_type=body.feedback_type,
            feedback_reason=body.feedback_reason,
        )
    except DuplicateArticleFeedbackError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Feedback already submitted for this article and department",
        ) from exc

    db.commit()
    return FeedbackCreateResponse(
        id=row.feedback_id,
        artifact_id=row.artifact_id,
        department_name=row.department_name,
        feedback_type=row.feedback_type,  # type: ignore[arg-type]
        feedback_reason=row.feedback_reason,  # type: ignore[arg-type]
        created_at=row.created_at,
    )
