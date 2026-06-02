#!/usr/bin/env python3
"""Sprint 4 verification: strategic scoring for validated enrichments."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_SRC = _BACKEND_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from xerago_intelligence.config import get_settings
from xerago_intelligence.db import dispose_engine, probe_connection, session_scope
from xerago_intelligence.db.repositories.enrichment_repository import EnrichmentRepository
from xerago_intelligence.scoring import ScoreInput, StrategicScorer

SCHEMA_DIR = _BACKEND_ROOT / "db" / "schema"


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )


def _apply_schemas() -> None:
    from sqlalchemy import text

    from xerago_intelligence.db import get_engine

    for path in sorted(SCHEMA_DIR.glob("*.sql")):
        sql = path.read_text(encoding="utf-8")
        statements = [
            s.strip()
            for s in sql.split(";")
            if s.strip() and not s.strip().startswith("--")
        ]
        engine = get_engine()
        try:
            with engine.begin() as conn:
                for statement in statements:
                    conn.execute(text(statement))
        except Exception as exc:
            if "artifact_enrichments_scoring" in path.name and "Duplicate column" in str(
                exc
            ):
                print(f"  (skip) {path.name} — columns already exist", flush=True)
                continue
            if "artifact_enrichments_validation" in path.name and "Duplicate column" in str(
                exc
            ):
                print(f"  (skip) {path.name} — columns already exist", flush=True)
                continue
            raise


def main() -> int:
    _configure_logging()
    failures = 0

    print("Xerago Intelligence Engine — Sprint 4 verification", flush=True)
    print("=" * 56, flush=True)

    settings = get_settings()

    print("\n[1/5] MySQL", flush=True)
    settings.log_mysql_startup()
    if not probe_connection().ok:
        print("  FAIL: MySQL connection", flush=True)
        return 1
    print("  MySQL: OK", flush=True)

    print("\n[2/5] Schema (incl. scoring columns)", flush=True)
    try:
        _apply_schemas()
        print("  Schema: OK", flush=True)
    except Exception as exc:
        print(f"  FAIL: {exc}", flush=True)
        return 1

    print("\n[3/5] Load latest validated enrichment", flush=True)
    artifact_id: str | None = None
    try:
        with session_scope() as session:
            pair = EnrichmentRepository(session).get_latest_with_artifact()
            if pair is None:
                print(
                    "  FAIL: No artifact_enrichments row. Run Sprint 3A/3B first.",
                    flush=True,
                )
                return 1
            enrichment, artifact = pair
            artifact_id = enrichment.artifact_id
            print(f"  artifact_id:       {enrichment.artifact_id}", flush=True)
            print(f"  domain:            {enrichment.domain}", flush=True)
            print(f"  signal_type:       {enrichment.signal_type}", flush=True)
            print(f"  confidence_score:  {enrichment.confidence_score}", flush=True)
            print(f"  validation_status: {enrichment.validation_status}", flush=True)
            print(f"  published_at:      {artifact.published_at}", flush=True)
    except Exception as exc:
        print(f"  FAIL: {exc}", flush=True)
        return 1

    print("\n[4/5] Calculate and save strategic score", flush=True)
    try:
        with session_scope() as session:
            pair = EnrichmentRepository(session).get_latest_with_artifact()
            assert pair is not None
            enrichment, artifact = pair

            scorer = StrategicScorer()
            result = scorer.score(
                ScoreInput(
                    confidence_score=enrichment.confidence_score,
                    domain=enrichment.domain,
                    signal_type=enrichment.signal_type,
                    published_at=artifact.published_at,
                )
            )

            print(f"  strategic_score: {result.strategic_score}", flush=True)
            print(f"  priority_level:  {result.priority_level}", flush=True)
            print(f"  score_reason:    {result.score_reason}", flush=True)

            updated = EnrichmentRepository(session).update_score(
                enrichment.artifact_id,
                strategic_score=result.strategic_score,
                priority_level=result.priority_level,
                score_reason=result.score_reason,
            )
            if updated is None:
                print("  FAIL: Could not persist score.", flush=True)
                failures += 1

    except Exception as exc:
        print(f"  FAIL: {exc}", flush=True)
        import traceback

        traceback.print_exc()
        failures += 1

    print("\n[5/5] Verify persisted scoring fields", flush=True)
    try:
        with session_scope() as session:
            row = EnrichmentRepository(session).get_by_artifact_id(artifact_id)
            if row is None:
                print("  FAIL: Enrichment row missing.", flush=True)
                failures += 1
            elif row.strategic_score is None:
                print("  FAIL: strategic_score not set.", flush=True)
                failures += 1
            elif not row.priority_level:
                print("  FAIL: priority_level not set.", flush=True)
                failures += 1
            elif not row.score_reason:
                print("  FAIL: score_reason empty.", flush=True)
                failures += 1
            elif row.scored_at is None:
                print("  FAIL: scored_at not set.", flush=True)
                failures += 1
            else:
                print(f"  strategic_score: {row.strategic_score}", flush=True)
                print(f"  priority_level:  {row.priority_level}", flush=True)
                print(f"  scored_at:       {row.scored_at}", flush=True)
                print(
                    f"  score_reason:    {row.score_reason[:200]}…"
                    if len(row.score_reason) > 200
                    else f"  score_reason:    {row.score_reason}",
                    flush=True,
                )
    except Exception as exc:
        print(f"  FAIL: {exc}", flush=True)
        failures += 1

    dispose_engine()

    print("\n" + "=" * 56, flush=True)
    if failures:
        print(f"FAILED ({failures} check(s))", flush=True)
        return 1
    print(
        "SUCCESS — strategic score and priority stored in artifact_enrichments.",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
