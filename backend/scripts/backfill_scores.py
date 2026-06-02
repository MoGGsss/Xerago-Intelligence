#!/usr/bin/env python3
"""Backfill Sprint 4 strategic scoring fields for existing enrichments."""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_SRC = _BACKEND_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from xerago_intelligence.db import dispose_engine, session_scope
from xerago_intelligence.db.models.artifact import Artifact
from xerago_intelligence.db.models.artifact_enrichment import ArtifactEnrichment
from xerago_intelligence.db.repositories.enrichment_repository import EnrichmentRepository
from xerago_intelligence.scoring import ScoreInput, StrategicScorer

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BackfillStats:
    total: int
    scored: int
    skipped: int
    failed: int


def _configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )


def _is_already_scored(row: ArtifactEnrichment) -> bool:
    return (
        row.strategic_score is not None
        and bool(row.priority_level)
        and bool(row.score_reason)
        and row.scored_at is not None
    )


def _load_artifact_ids() -> list[str]:
    with session_scope() as session:
        return list(
            session.scalars(
                select(ArtifactEnrichment.artifact_id).order_by(
                    ArtifactEnrichment.enriched_at.asc()
                )
            )
        )


def _process_artifact(artifact_id: str, scorer: StrategicScorer) -> str:
    with session_scope() as session:
        pair = session.execute(
            select(ArtifactEnrichment, Artifact)
            .join(Artifact, ArtifactEnrichment.artifact_id == Artifact.artifact_id)
            .where(ArtifactEnrichment.artifact_id == artifact_id)
            .limit(1)
        ).first()
        if pair is None:
            raise RuntimeError(f"Enrichment/artifact pair missing for {artifact_id}")

        enrichment, artifact = pair
        if _is_already_scored(enrichment):
            return "skipped"

        result = scorer.score(
            ScoreInput(
                confidence_score=enrichment.confidence_score,
                domain=enrichment.domain,
                signal_type=enrichment.signal_type,
                published_at=artifact.published_at,
            )
        )

        updated = EnrichmentRepository(session).update_score(
            enrichment.artifact_id,
            strategic_score=result.strategic_score,
            priority_level=result.priority_level,
            score_reason=result.score_reason,
        )
        if updated is None:
            raise RuntimeError(f"Failed to persist score for {artifact_id}")
        return "scored"


def run_backfill(*, verbose: bool = False) -> BackfillStats:
    _configure_logging(verbose)
    scorer = StrategicScorer()

    artifact_ids = _load_artifact_ids()
    total = len(artifact_ids)
    scored = 0
    skipped = 0
    failed = 0

    print("Backfill strategic scoring for artifact_enrichments", flush=True)
    print("=" * 56, flush=True)
    print(f"Total rows discovered: {total}", flush=True)

    for idx, artifact_id in enumerate(artifact_ids, start=1):
        try:
            status = _process_artifact(artifact_id, scorer)
            if status == "skipped":
                skipped += 1
                print(f"[{idx}/{total}] skip   {artifact_id} (already scored)", flush=True)
            else:
                scored += 1
                print(f"[{idx}/{total}] scored {artifact_id}", flush=True)
        except Exception as exc:  # noqa: BLE001
            failed += 1
            logger.exception("Backfill failed for artifact_id=%s", artifact_id)
            print(f"[{idx}/{total}] fail   {artifact_id} ({exc})", flush=True)

    print("\n" + "=" * 56, flush=True)
    print(
        f"Complete: total={total} scored={scored} skipped={skipped} failed={failed}",
        flush=True,
    )
    return BackfillStats(total=total, scored=scored, skipped=skipped, failed=failed)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Backfill strategic scoring fields for artifact_enrichments."
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging for troubleshooting.",
    )
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    stats = run_backfill(verbose=args.verbose)
    dispose_engine()
    return 1 if stats.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
