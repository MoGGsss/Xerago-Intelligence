"""Strategic scoring data models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ScoreInput:
    """Inputs for strategic score calculation."""

    confidence_score: int
    domain: str
    signal_type: str
    published_at: datetime


@dataclass(frozen=True)
class ScoreBreakdown:
    domain_points: int
    signal_points: int
    confidence_points: float
    recency_points: int
    age_days: int
    domain_key: str
    signal_key: str


@dataclass(frozen=True)
class ScoreResult:
    strategic_score: int
    priority_level: str
    score_reason: str
    breakdown: ScoreBreakdown
