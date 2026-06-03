#!/usr/bin/env python3
"""Evaluate negative filter for artifacts without a current filter decision."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from sqlalchemy import select

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_SRC = _BACKEND_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from xerago_intelligence.db import dispose_engine, get_session_factory
from xerago_intelligence.db.models.artifact import Artifact
from xerago_intelligence.db.models.artifact_filter_decision import ArtifactFilterDecision
from xerago_intelligence.filtering.filter_service import NegativeFilterService
from xerago_intelligence.filtering.negative_keywords import NEGATIVE_FILTER_VERSION

logger = logging.getLogger(__name__)


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )


def _artifact_ids_needing_evaluation(force: bool) -> list[str]:
    with get_session_factory()() as session:
        if force:
            return list(
                session.scalars(
                    select(Artifact.artifact_id).order_by(Artifact.ingested_at.asc())
                ).all()
            )
        return list(
            session.scalars(
                select(Artifact.artifact_id)
                .outerjoin(
                    ArtifactFilterDecision,
                    Artifact.artifact_id == ArtifactFilterDecision.artifact_id,
                )
                .where(ArtifactFilterDecision.artifact_id.is_(None))
                .order_by(Artifact.ingested_at.asc())
            ).all()
        )


def main() -> int:
    _configure_logging()
    force = "--force" in sys.argv
    session_factory = get_session_factory()
    artifact_ids = _artifact_ids_needing_evaluation(force)

    passed = 0
    skipped = 0
    print(
        f"Negative filter backfill ({NEGATIVE_FILTER_VERSION}) — {len(artifact_ids)} artifacts",
        flush=True,
    )

    for index, artifact_id in enumerate(artifact_ids, start=1):
        with session_factory() as session:
            service = NegativeFilterService(session)
            result = service.evaluate_and_persist(artifact_id, force=force)
            session.commit()
            if result.should_skip:
                skipped += 1
                print(f"SKIP {artifact_id} — {result.skip_reason}", flush=True)
            else:
                passed += 1

        if index % 100 == 0 or index == len(artifact_ids):
            print(f"Progress {index}/{len(artifact_ids)}", flush=True)

    print(f"Done passed={passed} skipped={skipped}", flush=True)
    dispose_engine()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
