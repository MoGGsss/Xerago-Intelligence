#!/usr/bin/env python3
"""Apply all SQL schemas under backend/db/schema/ (idempotent)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_SRC = _BACKEND_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

SCHEMA_DIR = _BACKEND_ROOT / "db" / "schema"
SCHEMA_FILES = (
    "artifacts.sql",
    "ingest_cursors.sql",
    "artifact_enrichments.sql",
    "artifact_enrichments_validation.sql",
    "artifact_enrichments_scoring.sql",
    "artifact_department_mappings.sql",
    "artifact_department_mappings_impact.sql",
    "artifact_filter_decisions.sql",
    "article_feedback.sql",
    "rss_sources.sql",
    "intelligence_runs.sql",
)

# MySQL errno values for idempotent "already applied" outcomes.
_IDEMPOTENT_ERRNOS = frozenset(
    {
        1050,  # ER_TABLE_EXISTS_ERROR — table already exists
        1060,  # ER_DUP_FIELDNAME — duplicate column name
        1061,  # ER_DUP_KEYNAME — duplicate key / index name
        1826,  # ER_FK_DUP_NAME — duplicate foreign key constraint name
        3822,  # ER_CHECK_CONSTRAINT_DUP_NAME — duplicate check constraint (8.0.16+)
    }
)

_ALREADY_APPLIED_PHRASES = (
    "duplicate column name",
    "duplicate key name",
    "duplicate index",
    "duplicate foreign key constraint",
    "duplicate check constraint",
    "duplicate constraint",
    "constraint already exists",
    "already exists",
)


def _mysql_errno(exc: BaseException) -> int | None:
    for target in (exc, getattr(exc, "orig", None)):
        if target is None:
            continue
        args = getattr(target, "args", None)
        if args and isinstance(args[0], int):
            return args[0]
    return None


def _exception_messages(exc: BaseException) -> str:
    parts: list[str] = [str(exc)]
    orig = getattr(exc, "orig", None)
    if orig is not None:
        parts.append(str(orig))
    return " ".join(parts).lower()


def _is_already_applied(exc: BaseException) -> bool:
    if _mysql_errno(exc) in _IDEMPOTENT_ERRNOS:
        return True
    message = _exception_messages(exc)
    return any(phrase in message for phrase in _ALREADY_APPLIED_PHRASES)


def _split_statements(sql: str) -> list[str]:
    return [
        s.strip()
        for s in sql.split(";")
        if s.strip() and not s.strip().startswith("--")
    ]


_ALTER_TABLE_RE = re.compile(r"^ALTER\s+TABLE\s+(\S+)", re.IGNORECASE | re.DOTALL)
_ADD_COLUMN_SPLIT_RE = re.compile(r",\s*(?=ADD\s+COLUMN\b)", re.IGNORECASE)


def _expand_alter_add_columns(statement: str) -> list[str]:
    """
    Split multi-column ALTER TABLE ... ADD COLUMN into one statement per column.

    If the first column already exists, later columns can still be applied.
    """
    if _ADD_COLUMN_SPLIT_RE.search(statement) is None:
        return [statement]
    match = _ALTER_TABLE_RE.match(statement.strip())
    if match is None:
        return [statement]
    table_name = match.group(1)
    parts = _ADD_COLUMN_SPLIT_RE.split(statement.strip())
    expanded: list[str] = []
    for index, part in enumerate(parts):
        fragment = part.strip().rstrip(",")
        if index == 0:
            expanded.append(fragment)
        else:
            expanded.append(f"ALTER TABLE {table_name} {fragment}")
    return expanded


def _expand_statements(statements: list[str]) -> list[str]:
    expanded: list[str] = []
    for statement in statements:
        expanded.extend(_expand_alter_add_columns(statement))
    return expanded


def _execute_statement(engine, statement: str) -> bool:
    """Execute one statement. Returns True if applied, False if skipped."""
    from sqlalchemy import text

    try:
        with engine.begin() as conn:
            conn.execute(text(statement))
        return True
    except Exception as exc:
        if _is_already_applied(exc):
            print("SKIP: already applied")
            return False
        raise


def _apply_file(engine, name: str, path: Path) -> tuple[int, int]:
    sql = path.read_text(encoding="utf-8")
    statements = _expand_statements(_split_statements(sql))
    applied = 0
    skipped = 0
    for statement in statements:
        if _execute_statement(engine, statement):
            applied += 1
        else:
            skipped += 1
    return applied, skipped


def main() -> int:
    from xerago_intelligence.config import get_settings
    from xerago_intelligence.db import dispose_engine, get_engine, probe_connection

    settings = get_settings()
    settings.log_mysql_startup()
    if not probe_connection().ok:
        print("FAIL: Cannot connect to MySQL.")
        return 1

    engine = get_engine()
    try:
        for name in SCHEMA_FILES:
            path = SCHEMA_DIR / name
            if not path.is_file():
                print(f"FAIL: Missing {path}")
                return 1
            try:
                applied, skipped = _apply_file(engine, name, path)
            except Exception as exc:
                print(f"FAIL: {name} — {exc}")
                return 1
            if applied:
                suffix = f" ({skipped} skipped)" if skipped else ""
                print(f"OK: Applied {name}{suffix}")
            elif skipped:
                print(f"OK: {name} (already applied)")
            else:
                print(f"OK: {name}")
    finally:
        dispose_engine()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
