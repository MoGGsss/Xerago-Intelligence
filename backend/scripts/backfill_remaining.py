#!/usr/bin/env python3
"""Backfill missing enrichments and scoring for existing artifacts."""

from __future__ import annotations

import logging
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_SRC = _BACKEND_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from xerago_intelligence.db import dispose_engine, get_session_factory
from xerago_intelligence.db.models.artifact import Artifact
from xerago_intelligence.db.models.artifact_enrichment import ArtifactEnrichment
from xerago_intelligence.db.repositories.enrichment_repository import EnrichmentRepository
from xerago_intelligence.enrichment.service import ArtifactEnrichmentService
from xerago_intelligence.filtering import EnrichmentSkippedError
from xerago_intelligence.scoring import ScoreInput, StrategicScorer

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BackfillSummary:
    total: int
    succeeded: int
    skipped_negative: int
    failed: int
    elapsed_time: str


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )


def _find_artifacts_missing_enrichment() -> list[str]:
    session_factory = get_session_factory()
    with session_factory() as session:
        rows = session.scalars(
            select(Artifact.artifact_id)
            .outerjoin(
                ArtifactEnrichment,
                Artifact.artifact_id == ArtifactEnrichment.artifact_id,
            )
            .where(ArtifactEnrichment.artifact_id.is_(None))
            .order_by(Artifact.ingested_at.asc())
        ).all()
    return list(rows)


def _format_elapsed(elapsed_seconds: float) -> str:
    total_seconds = int(round(elapsed_seconds))
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def _process_one_artifact(artifact_id: str) -> None:
    session_factory = get_session_factory()
    with session_factory() as session:
        service = ArtifactEnrichmentService(session)
        repo = EnrichmentRepository(session)
        scorer = StrategicScorer()

        result = service.enrich_artifact(artifact_id)
        artifact = service.get_artifact(artifact_id)
        if artifact is None:
            raise RuntimeError(f"Artifact not found after enrichment: {artifact_id}")

        score_result = scorer.score(
            ScoreInput(
                confidence_score=result.confidence_score,
                domain=result.payload.domain,
                signal_type=result.payload.signal_type,
                published_at=artifact.published_at,
            )
        )

        updated = repo.update_score(
            artifact_id,
            strategic_score=score_result.strategic_score,
            priority_level=score_result.priority_level,
            score_reason=score_result.score_reason,
        )
        if updated is None:
            raise RuntimeError(f"Failed to persist scoring for artifact: {artifact_id}")

        session.commit()


def run_backfill() -> BackfillSummary:
    _configure_logging()
    started_at = time.monotonic()

    artifact_ids = _find_artifacts_missing_enrichment()
    total = len(artifact_ids)
    succeeded = 0
    skipped_negative = 0
    failed = 0

    print("Backfill remaining artifacts (enrichment + scoring)", flush=True)
    print("=" * 64, flush=True)
    print(f"Total missing enrichment: {total}", flush=True)

    for idx, artifact_id in enumerate(artifact_ids, start=1):
        try:
            _process_one_artifact(artifact_id)
            succeeded += 1
        except EnrichmentSkippedError as exc:
            skipped_negative += 1
            print(
                f"[{idx}/{total}] SKIP   {artifact_id} — {exc.result.skip_reason}",
                flush=True,
            )
        except Exception as exc:  # noqa: BLE001
            failed += 1
            logger.exception("Failed artifact_id=%s", artifact_id)
            print(f"[{idx}/{total}] FAILED  {artifact_id} — {exc}", flush=True)
            continue

        if idx % 10 == 0 or idx == total:
            print(
                f"[{idx}/{total}] progress succeeded={succeeded} "
                f"skipped_negative={skipped_negative} failed={failed}",
                flush=True,
            )

    elapsed = _format_elapsed(time.monotonic() - started_at)
    return BackfillSummary(
        total=total,
        succeeded=succeeded,
        skipped_negative=skipped_negative,
        failed=failed,
        elapsed_time=elapsed,
    )


def main() -> int:
    summary = run_backfill()
    dispose_engine()

    print("\nFinal summary", flush=True)
    print("=" * 64, flush=True)
    print(f"total:       {summary.total}", flush=True)
    print(f"succeeded:   {summary.succeeded}", flush=True)
    print(f"skipped_neg: {summary.skipped_negative}", flush=True)
    print(f"failed:      {summary.failed}", flush=True)
    print(f"elapsed_time:{summary.elapsed_time}", flush=True)

    return 1 if summary.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
