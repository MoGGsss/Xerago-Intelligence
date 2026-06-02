"""Strategic scoring engine."""

from __future__ import annotations

from datetime import datetime, timezone

from xerago_intelligence.scoring.models import ScoreBreakdown, ScoreInput, ScoreResult
from xerago_intelligence.scoring.weights import (
    CONFIDENCE_MULTIPLIER,
    domain_weight,
    priority_for_score,
    recency_points,
    resolve_domain_key,
    resolve_signal_key,
    signal_weight,
)


class StrategicScorer:
    """Compute strategic_score and priority_level from enrichment inputs."""

    def score(
        self,
        inputs: ScoreInput,
        *,
        reference_time: datetime | None = None,
    ) -> ScoreResult:
        now = _as_naive_utc(reference_time or datetime.now(timezone.utc))
        published = _as_naive_utc(inputs.published_at)
        age_days = max(0, (now.date() - published.date()).days)

        domain_key = resolve_domain_key(inputs.domain)
        signal_key = resolve_signal_key(inputs.signal_type)
        domain_pts = domain_weight(inputs.domain)
        signal_pts = signal_weight(inputs.signal_type)
        confidence_pts = max(0, inputs.confidence_score) * CONFIDENCE_MULTIPLIER
        recency_pts = recency_points(age_days)

        raw_total = domain_pts + signal_pts + confidence_pts + recency_pts
        strategic_score = int(round(max(0, min(100, raw_total))))
        priority_level = priority_for_score(strategic_score)

        breakdown = ScoreBreakdown(
            domain_points=domain_pts,
            signal_points=signal_pts,
            confidence_points=confidence_pts,
            recency_points=recency_pts,
            age_days=age_days,
            domain_key=domain_key,
            signal_key=signal_key,
        )

        score_reason = (
            f"domain={inputs.domain}->{domain_key} (+{domain_pts}); "
            f"signal_type={inputs.signal_type}->{signal_key} (+{signal_pts}); "
            f"confidence={inputs.confidence_score}*{CONFIDENCE_MULTIPLIER} "
            f"(+{confidence_pts:.1f}); "
            f"recency={age_days}d (+{recency_pts}); "
            f"total={strategic_score}"
        )

        return ScoreResult(
            strategic_score=strategic_score,
            priority_level=priority_level,
            score_reason=score_reason,
            breakdown=breakdown,
        )


def _as_naive_utc(value: datetime) -> datetime:
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value
