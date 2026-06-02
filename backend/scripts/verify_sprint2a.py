#!/usr/bin/env python3
"""Sprint 2A verification: RSS ingest into MySQL artifacts table."""

from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_SRC = _BACKEND_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from xerago_intelligence.config import get_settings
from xerago_intelligence.db import dispose_engine, probe_connection, session_scope
from xerago_intelligence.db.repositories.artifact_repository import ArtifactRepository
from xerago_intelligence.ingest.diagnostics import enable_diagnostics, emit, timed_step
from xerago_intelligence.ingest.rss import (
    DEFAULT_TEST_SOURCE_ID,
    OPENAI_NEWS_RSS,
    RssIngestionService,
)

SCHEMA_FILE = _BACKEND_ROOT / "db" / "schema" / "artifacts.sql"


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )
    enable_diagnostics(True)


def _apply_schema() -> None:
    from sqlalchemy import text

    from xerago_intelligence.db import get_engine

    sql = SCHEMA_FILE.read_text(encoding="utf-8")
    statements = [
        s.strip()
        for s in sql.split(";")
        if s.strip() and not s.strip().startswith("--")
    ]
    engine = get_engine()
    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))


def main() -> int:
    _configure_logging()

    print("Xerago Intelligence Engine — Sprint 2A verification", flush=True)
    print("=" * 56, flush=True)

    settings = get_settings()
    failures = 0

    print("\n[1/4] MySQL", flush=True)
    with timed_step("MySQL probe"):
        settings.log_mysql_startup()
        if not probe_connection().ok:
            print("  FAIL: MySQL connection", flush=True)
            return 1
    print("  MySQL: OK", flush=True)

    print("\n[2/4] Schema", flush=True)
    try:
        with timed_step("Apply artifacts schema"):
            _apply_schema()
        print(f"  Applied: {SCHEMA_FILE.name}", flush=True)
    except Exception as exc:
        print(f"  FAIL: {exc}", flush=True)
        return 1

    print(f"\n[3/4] RSS ingest — {OPENAI_NEWS_RSS}", flush=True)
    print(f"  source_id: {DEFAULT_TEST_SOURCE_ID}", flush=True)
    emit("[diag] Beginning first ingest run")

    try:
        ingest_started = time.perf_counter()
        with timed_step("First ingest run (session_scope)"):
            with session_scope() as session:
                emit("[diag] DB session opened")
                repo = ArtifactRepository(session)
                count_before = repo.count_by_source(DEFAULT_TEST_SOURCE_ID)
                emit(f"[diag] Rows in DB before ingest: {count_before}")

                service = RssIngestionService(session)
                try:
                    result_first = service.ingest_feed(
                        OPENAI_NEWS_RSS, DEFAULT_TEST_SOURCE_ID
                    )
                finally:
                    service.close()

                count_after_first = repo.count_by_source(DEFAULT_TEST_SOURCE_ID)
                emit(f"[diag] Rows visible in session after ingest: {count_after_first}")
                emit("[diag] DB session committing transaction")

            emit("[diag] DB session committed (first run)")

        with timed_step("Second ingest run (session_scope)"):
            with session_scope() as session:
                service = RssIngestionService(session)
                try:
                    result_second = service.ingest_feed(
                        OPENAI_NEWS_RSS, DEFAULT_TEST_SOURCE_ID
                    )
                finally:
                    service.close()
            emit("[diag] DB session committed (second run)")

        ingest_elapsed = time.perf_counter() - ingest_started
        emit(f"[diag] Total ingest phase elapsed: {ingest_elapsed:.3f}s")

        print(f"\n  --- First run summary ---", flush=True)
        print(f"  HTTP status:              {result_first.http_status}", flush=True)
        print(f"  Content length:           {result_first.content_length} bytes", flush=True)
        print(f"  Entries found:            {result_first.fetched_entries}", flush=True)
        print(f"  Inserts attempted:        {result_first.inserts_attempted}", flush=True)
        print(f"  Inserts committed:        {result_first.inserts_committed}", flush=True)
        print(f"  Skipped duplicates:       {result_first.skipped_duplicates}", flush=True)
        print(f"  Skipped invalid:          {result_first.skipped_invalid}", flush=True)
        print(f"  Rows before:              {count_before}", flush=True)
        print(f"  Rows after 1st run:       {count_after_first}", flush=True)
        print(f"\n  --- Second run summary ---", flush=True)
        print(f"  Inserted (2nd run):       {result_second.inserted}", flush=True)
        print(f"  Skipped duplicates:       {result_second.skipped_duplicates}", flush=True)

        if count_after_first <= count_before:
            print("  FAIL: No new articles were stored on first run.", flush=True)
            failures += 1
        if result_second.inserted != 0:
            print("  FAIL: Second run inserted duplicates (expected 0 new rows).", flush=True)
            failures += 1

    except Exception as exc:
        print(f"  FAIL: {exc}", flush=True)
        import traceback

        traceback.print_exc()
        failures += 1
        dispose_engine()
        return 1

    print("\n[4/4] Sample stored articles", flush=True)
    try:
        with timed_step("List sample articles"):
            with session_scope() as session:
                repo = ArtifactRepository(session)
                samples = repo.list_recent(limit=3, source_id=DEFAULT_TEST_SOURCE_ID)
                for item in samples:
                    print(f"  - {item.title[:80]}", flush=True)
                    print(f"    url: {item.url[:100]}", flush=True)
                    print(
                        f"    published_at: {item.published_at} | "
                        f"ingested_at: {item.ingested_at}",
                        flush=True,
                    )
    except Exception as exc:
        print(f"  FAIL listing samples: {exc}", flush=True)
        failures += 1

    dispose_engine()

    print("\n" + "=" * 56, flush=True)
    if failures:
        print(f"FAILED ({failures} check(s))", flush=True)
        return 1
    print("SUCCESS — RSS articles ingested and stored in artifacts table.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
