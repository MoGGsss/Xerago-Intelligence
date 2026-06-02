#!/usr/bin/env python3
"""Sprint 3B verification: validate enrichment classifications and store confidence."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_SRC = _BACKEND_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from xerago_intelligence.classification import ClassificationValidator
from xerago_intelligence.classification.confidence import (
    calculate_confidence,
    validation_status_for_confidence,
)
from xerago_intelligence.config import get_settings
from xerago_intelligence.db import dispose_engine, probe_connection, session_scope
from xerago_intelligence.db.repositories.enrichment_repository import EnrichmentRepository
from xerago_intelligence.enrichment.service import ArtifactEnrichmentService

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
            if "artifact_enrichments_validation" in path.name and "Duplicate column" in str(
                exc
            ):
                print(f"  (skip) {path.name} — columns already exist", flush=True)
                continue
            raise


def main() -> int:
    _configure_logging()
    failures = 0

    print("Xerago Intelligence Engine — Sprint 3B verification", flush=True)
    print("=" * 56, flush=True)

    settings = get_settings()

    print("\n[1/5] MySQL", flush=True)
    settings.log_mysql_startup()
    if not probe_connection().ok:
        print("  FAIL: MySQL connection", flush=True)
        return 1
    print("  MySQL: OK", flush=True)

    print("\n[2/5] Schema (incl. validation columns)", flush=True)
    try:
        _apply_schemas()
        print("  Schema: OK", flush=True)
    except Exception as exc:
        print(f"  FAIL: {exc}", flush=True)
        return 1

    print("\n[3/5] Load enriched artifact", flush=True)
    artifact_id: str | None = None
    try:
        with session_scope() as session:
            row = EnrichmentRepository(session).get_latest()
            if row is None:
                print(
                    "  FAIL: No artifact_enrichments row. Run verify_sprint3a.py first.",
                    flush=True,
                )
                return 1
            artifact_id = row.artifact_id
            print(f"  artifact_id:     {row.artifact_id}", flush=True)
            print(f"  domain:          {row.domain}", flush=True)
            print(f"  signal_type:     {row.signal_type}", flush=True)
            print(f"  prompt_version:  {row.prompt_version}", flush=True)
    except Exception as exc:
        print(f"  FAIL: {exc}", flush=True)
        return 1

    print("\n[4/5] Validate classifications (categories.md)", flush=True)
    try:
        categories_path = settings.resolve_project_root() / "docs" / "categories.md"
        validator = ClassificationValidator.from_categories_file(categories_path)

        with session_scope() as session:
            row = EnrichmentRepository(session).get_by_artifact_id(artifact_id)
            assert row is not None
            validation = validator.validate(row.domain, row.signal_type)
            confidence = calculate_confidence(validation)
            status = validation_status_for_confidence(confidence)

            print(f"  domain match:      {validation.domain.level.value}", flush=True)
            print(f"  signal_type match: {validation.signal_type.level.value}", flush=True)
            print(f"  confidence_score:  {confidence}", flush=True)
            print(f"  validation_status: {status}", flush=True)

            service = ArtifactEnrichmentService(session, validator=validator)
            updated = service.validate_and_update(artifact_id)
            if updated is None:
                print("  FAIL: Could not update enrichment row.", flush=True)
                failures += 1
            else:
                print(f"  classification_reason:", flush=True)
                print(f"    {updated.classification_reason}", flush=True)

    except Exception as exc:
        print(f"  FAIL: {exc}", flush=True)
        import traceback

        traceback.print_exc()
        failures += 1

    print("\n[5/5] Verify persisted validation fields", flush=True)
    try:
        with session_scope() as session:
            row = EnrichmentRepository(session).get_by_artifact_id(artifact_id)
            if row is None:
                print("  FAIL: Enrichment row missing.", flush=True)
                failures += 1
            elif row.validation_status == "pending":
                print("  FAIL: validation_status still pending.", flush=True)
                failures += 1
            elif row.confidence_score is None:
                print("  FAIL: confidence_score not set.", flush=True)
                failures += 1
            elif not row.classification_reason:
                print("  FAIL: classification_reason empty.", flush=True)
                failures += 1
            else:
                print(f"  confidence_score:      {row.confidence_score}", flush=True)
                print(f"  validation_status:     {row.validation_status}", flush=True)
                print(
                    f"  classification_reason: {row.classification_reason[:200]}…"
                    if len(row.classification_reason) > 200
                    else f"  classification_reason: {row.classification_reason}",
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
        "SUCCESS — classification validated; confidence and status stored in MySQL.",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
