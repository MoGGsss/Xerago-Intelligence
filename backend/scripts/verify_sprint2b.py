#!/usr/bin/env python3
"""Sprint 2B verification: incremental RSS ingest with ingest_cursors."""

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
from xerago_intelligence.db.repositories.artifact_repository import ArtifactRepository
from xerago_intelligence.db.repositories.cursor_repository import CursorRepository
from xerago_intelligence.ingest.diagnostics import enable_diagnostics, emit
from xerago_intelligence.ingest.rss import (
    DEFAULT_TEST_SOURCE_ID,
    OPENAI_NEWS_RSS,
    RssIngestionService,
)

SCHEMA_DIR = _BACKEND_ROOT / "db" / "schema"


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )
    enable_diagnostics(True)


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
        with engine.begin() as conn:
            for statement in statements:
                conn.execute(text(statement))


def _print_result(label: str, result) -> None:
    print(f"\n  --- {label} ---", flush=True)
    print(f"  fetched:          {result.fetched}", flush=True)
    print(f"  processed:        {result.processed}", flush=True)
    print(f"  inserted:         {result.inserted}", flush=True)
    print(f"  skipped:          {result.skipped}", flush=True)
    print(f"    skipped_cursor:   {result.skipped_cursor}", flush=True)
    print(f"    skipped_duplicate:{result.skipped_duplicate}", flush=True)
    print(f"    skipped_invalid:  {result.skipped_invalid}", flush=True)


def main() -> int:
    _configure_logging()

    print("Xerago Intelligence Engine — Sprint 2B verification", flush=True)
    print("=" * 56, flush=True)

    settings = get_settings()
    failures = 0

    print("\n[1/5] MySQL", flush=True)
    settings.log_mysql_startup()
    if not probe_connection().ok:
        print("  FAIL: MySQL connection", flush=True)
        return 1
    print("  MySQL: OK", flush=True)

    print("\n[2/5] Schema", flush=True)
    try:
        _apply_schemas()
        print("  Schema: OK (artifacts + ingest_cursors)", flush=True)
    except Exception as exc:
        print(f"  FAIL: {exc}", flush=True)
        return 1

    print(f"\n[3/5] First ingest (establish cursor) — {OPENAI_NEWS_RSS}", flush=True)
    emit(f"source_id={DEFAULT_TEST_SOURCE_ID}")

    try:
        with session_scope() as session:
            service = RssIngestionService(session)
            try:
                result_first = service.ingest_feed(
                    OPENAI_NEWS_RSS, DEFAULT_TEST_SOURCE_ID
                )
            finally:
                service.close()
            cursor_row = CursorRepository(session).get_row(DEFAULT_TEST_SOURCE_ID)

        _print_result("First run", result_first)
        if cursor_row is None:
            print("  FAIL: ingest_cursors row not created after first run.", flush=True)
            failures += 1
        else:
            print(
                f"  Cursor saved: last_published_at={cursor_row.last_published_at}",
                flush=True,
            )

        if result_first.fetched == 0:
            print("  FAIL: Feed returned zero entries.", flush=True)
            failures += 1

    except Exception as exc:
        print(f"  FAIL: {exc}", flush=True)
        import traceback

        traceback.print_exc()
        dispose_engine()
        return 1

    print(f"\n[4/5] Second ingest (incremental) — {OPENAI_NEWS_RSS}", flush=True)
    try:
        with session_scope() as session:
            cursor_before = CursorRepository(session).get_state(DEFAULT_TEST_SOURCE_ID)
            emit(
                f"Cursor before 2nd run: "
                f"{cursor_before.last_published_at.isoformat() if cursor_before and cursor_before.last_published_at else 'none'}"
            )

            service = RssIngestionService(session)
            try:
                result_second = service.ingest_feed(
                    OPENAI_NEWS_RSS, DEFAULT_TEST_SOURCE_ID
                )
            finally:
                service.close()

        _print_result("Second run", result_second)

        if result_second.processed != 0:
            print(
                "  FAIL: Second run processed entries (expected 0 — cursor should skip history).",
                flush=True,
            )
            failures += 1
        if result_second.inserted != 0:
            print(
                "  FAIL: Second run inserted rows (expected 0 with unchanged feed).",
                flush=True,
            )
            failures += 1
        if result_second.skipped_cursor < result_second.fetched and result_second.fetched > 0:
            print(
                "  FAIL: Second run should skip historical items via cursor "
                f"(skipped_cursor={result_second.skipped_cursor}, "
                f"fetched={result_second.fetched}).",
                flush=True,
            )
            failures += 1
        if result_second.fetched > 0 and result_second.skipped_cursor == 0:
            print(
                "  WARN: No cursor skips — verify ingest_cursors table is populated.",
                flush=True,
            )

    except Exception as exc:
        print(f"  FAIL: {exc}", flush=True)
        import traceback

        traceback.print_exc()
        failures += 1

    print("\n[5/5] Cursor state in database", flush=True)
    try:
        with session_scope() as session:
            row = CursorRepository(session).get_row(DEFAULT_TEST_SOURCE_ID)
            if row:
                print(f"  source_id:         {row.source_id}", flush=True)
                print(f"  last_published_at: {row.last_published_at}", flush=True)
                print(f"  last_entry_id:     {row.last_entry_id}", flush=True)
                print(f"  updated_at:        {row.updated_at}", flush=True)
            else:
                print("  FAIL: No cursor row found.", flush=True)
                failures += 1
    except Exception as exc:
        print(f"  FAIL: {exc}", flush=True)
        failures += 1

    dispose_engine()

    print("\n" + "=" * 56, flush=True)
    if failures:
        print(f"FAILED ({failures} check(s))", flush=True)
        return 1
    print(
        "SUCCESS — incremental ingest uses cursor; second run skips historical content.",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
