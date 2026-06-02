#!/usr/bin/env python3
"""Apply Sprint 2A artifacts table schema to MySQL.

Prefer ``apply_schema.py`` for artifacts + ingest_cursors (Sprint 2B).
"""

from __future__ import annotations

import sys
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_SRC = _BACKEND_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from sqlalchemy import text

from xerago_intelligence.config import get_settings
from xerago_intelligence.db import dispose_engine, get_engine, probe_connection

SCHEMA_FILE = _BACKEND_ROOT / "db" / "schema" / "artifacts.sql"


def main() -> int:
    print("Applying artifacts schema...")
    settings = get_settings()
    settings.log_mysql_startup()

    if not probe_connection().ok:
        print("FAIL: Cannot connect to MySQL.")
        return 1

    if not SCHEMA_FILE.is_file():
        print(f"FAIL: Schema file not found: {SCHEMA_FILE}")
        return 1

    sql = SCHEMA_FILE.read_text(encoding="utf-8")
    statements = [
        statement.strip()
        for statement in sql.split(";")
        if statement.strip() and not statement.strip().startswith("--")
    ]

    engine = get_engine()
    with engine.begin() as connection:
        for statement in statements:
            if statement.upper().startswith("SET "):
                connection.execute(text(statement))
            else:
                connection.execute(text(statement))

    dispose_engine()
    print(f"OK: Applied {SCHEMA_FILE.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
