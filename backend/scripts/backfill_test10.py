#!/usr/bin/env python3
"""Temporary backfill test: enrich first 10 artifacts missing enrichment."""

from __future__ import annotations

import sys
from pathlib import Path
from time import perf_counter

from sqlalchemy import exists, select

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_SRC = _BACKEND_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from xerago_intelligence.db import session_scope
from xerago_intelligence.db.models.artifact import Artifact
from xerago_intelligence.db.models.artifact_enrichment import ArtifactEnrichment
from xerago_intelligence.enrichment.service import ArtifactEnrichmentService


def main() -> int:
    stmt = (
        select(Artifact.artifact_id, Artifact.title)
        .where(
            ~exists(
                select(1).where(
                    ArtifactEnrichment.artifact_id == Artifact.artifact_id
                )
            )
        )
        .order_by(Artifact.ingested_at.asc())
        .limit(10)
    )

    with session_scope() as session:
        targets = list(session.execute(stmt).all())

    total = len(targets)
    succeeded = 0
    failed = 0

    for index, (artifact_id, title) in enumerate(targets, 1):
        start = perf_counter()
        try:
            with session_scope() as session:
                ArtifactEnrichmentService(session).enrich_artifact(
                    str(artifact_id),
                    force=False,
                )
            elapsed = perf_counter() - start
            succeeded += 1
            print(
                f"[{index}/{total}] artifact_id={artifact_id} "
                f"| title={title} | status=success | elapsed_seconds={elapsed:.2f}",
                flush=True,
            )
        except Exception as exc:  # noqa: BLE001
            elapsed = perf_counter() - start
            failed += 1
            print(
                f"[{index}/{total}] artifact_id={artifact_id} "
                f"| title={title} | status=failure | elapsed_seconds={elapsed:.2f} "
                f"| error={exc}",
                flush=True,
            )

    print(
        f"summary total={total} succeeded={succeeded} failed={failed}",
        flush=True,
    )
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
