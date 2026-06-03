"""Tests for feedback API request validation."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from xerago_intelligence.api.schemas.feedback import FeedbackCreateRequest


def test_positive_feedback_omits_reason() -> None:
    req = FeedbackCreateRequest(
        artifact_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        department_name="MarTech",
        feedback_type="positive",
    )
    assert req.feedback_reason is None


def test_positive_feedback_rejects_reason() -> None:
    with pytest.raises(ValidationError):
        FeedbackCreateRequest(
            artifact_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            department_name="MarTech",
            feedback_type="positive",
            feedback_reason="not_relevant",
        )


def test_negative_feedback_requires_reason() -> None:
    with pytest.raises(ValidationError):
        FeedbackCreateRequest(
            artifact_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            department_name="MarTech",
            feedback_type="negative",
        )


def test_negative_feedback_accepts_reason() -> None:
    req = FeedbackCreateRequest(
        artifact_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        department_name="AI Engineering",
        feedback_type="negative",
        feedback_reason="too_technical",
    )
    assert req.feedback_reason == "too_technical"
