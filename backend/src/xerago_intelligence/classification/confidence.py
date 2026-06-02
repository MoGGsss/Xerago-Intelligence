"""Confidence scoring for classification validation."""

from __future__ import annotations

from xerago_intelligence.classification.validator import (
    ClassificationValidation,
    MatchLevel,
)

CONFIDENCE_EXACT = 100
CONFIDENCE_PARTIAL = 75
CONFIDENCE_UNCERTAIN = 50
CONFIDENCE_INVALID = 0

_LEVEL_SCORES: dict[MatchLevel, int] = {
    MatchLevel.EXACT: CONFIDENCE_EXACT,
    MatchLevel.PARTIAL: CONFIDENCE_PARTIAL,
    MatchLevel.UNCERTAIN: CONFIDENCE_UNCERTAIN,
    MatchLevel.INVALID: CONFIDENCE_INVALID,
}

STATUS_VALID = "valid"
STATUS_PARTIAL = "partial"
STATUS_UNCERTAIN = "uncertain"
STATUS_INVALID = "invalid"


def score_for_level(level: MatchLevel) -> int:
    return _LEVEL_SCORES[level]


def calculate_confidence(validation: ClassificationValidation) -> int:
    """
    Overall confidence from domain and signal_type checks.

    Uses the minimum of both field scores (conservative).
    """
    domain_score = score_for_level(validation.domain.level)
    signal_score = score_for_level(validation.signal_type.level)
    return min(domain_score, signal_score)


def validation_status_for_confidence(confidence_score: int) -> str:
    if confidence_score >= CONFIDENCE_EXACT:
        return STATUS_VALID
    if confidence_score >= CONFIDENCE_PARTIAL:
        return STATUS_PARTIAL
    if confidence_score >= CONFIDENCE_UNCERTAIN:
        return STATUS_UNCERTAIN
    return STATUS_INVALID


def build_classification_reason(validation: ClassificationValidation) -> str:
    parts = [
        f"domain={validation.domain.value} ({validation.domain.level.value}): "
        f"{validation.domain.detail}",
        f"signal_type={validation.signal_type.value} "
        f"({validation.signal_type.level.value}): {validation.signal_type.detail}",
    ]
    return "; ".join(parts)
