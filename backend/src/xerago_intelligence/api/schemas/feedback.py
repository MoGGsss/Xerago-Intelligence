"""Pydantic models for article feedback API."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

FeedbackType = Literal["positive", "negative"]
FeedbackReason = Literal[
    "wrong_department",
    "too_technical",
    "already_known",
    "low_business_impact",
    "duplicate_content",
    "not_relevant",
]

NEGATIVE_FEEDBACK_REASONS: frozenset[str] = frozenset(
    {
        "wrong_department",
        "too_technical",
        "already_known",
        "low_business_impact",
        "duplicate_content",
        "not_relevant",
    }
)


class FeedbackCreateRequest(BaseModel):
    artifact_id: str = Field(min_length=1, max_length=36)
    department_name: str = Field(min_length=1, max_length=64)
    feedback_type: FeedbackType
    feedback_reason: FeedbackReason | None = None

    @model_validator(mode="after")
    def validate_feedback_reason(self) -> FeedbackCreateRequest:
        if self.feedback_type == "positive":
            if self.feedback_reason is not None:
                raise ValueError("feedback_reason must be omitted for positive feedback")
        elif self.feedback_reason is None:
            raise ValueError("feedback_reason is required for negative feedback")
        return self


class FeedbackCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artifact_id: str
    department_name: str
    feedback_type: FeedbackType
    feedback_reason: FeedbackReason | None
    created_at: datetime
