#!/usr/bin/env python3
"""Apply all SQL schemas under backend/db/schema/."""

from __future__ import annotations

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
)


def main() -> int:
    from sqlalchemy import text

    from xerago_intelligence.config import get_settings
    from xerago_intelligence.db import dispose_engine, get_engine, probe_connection

    settings = get_settings()
    settings.log_mysql_startup()
    if not probe_connection().ok:
        print("FAIL: Cannot connect to MySQL.")
        return 1

    engine = get_engine()
    for name in SCHEMA_FILES:
        path = SCHEMA_DIR / name
        if not path.is_file():
            print(f"FAIL: Missing {path}")
            return 1
        sql = path.read_text(encoding="utf-8")
        statements = [
            s.strip()
            for s in sql.split(";")
            if s.strip() and not s.strip().startswith("--")
        ]
        with engine.begin() as conn:
            for statement in statements:
                conn.execute(text(statement))
        print(f"OK: Applied {name}")

    dispose_engine()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
