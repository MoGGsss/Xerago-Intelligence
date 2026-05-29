#!/usr/bin/env python3
"""Verify Python can connect to MySQL using backend settings."""

from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import quote_plus

# Allow running without editable install: backend/src on sys.path
_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_SRC = _BACKEND_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from xerago_intelligence.config import get_settings
from xerago_intelligence.db import check_connection, dispose_engine, get_engine


def main() -> int:
    settings = get_settings()
    url = settings.resolved_database_url()
    # Mask password in printed URL
    display_url = url
    if settings.mysql_password:
        display_url = display_url.replace(
            quote_plus(settings.mysql_password),
            "***",
        )

    print("Xerago Intelligence Engine — MySQL connectivity check")
    print(f"Target: {display_url}")
    print(f"Charset: {settings.mysql_charset}")

    if not check_connection():
        print("FAIL: Could not connect to MySQL.")
        print("Ensure MySQL is running, database exists, and .env is configured.")
        return 1

    try:
        with get_engine().connect() as conn:
            version_row = conn.execute(text("SELECT VERSION()")).scalar_one()
            db_row = conn.execute(text("SELECT DATABASE()")).scalar_one()
    except SQLAlchemyError as exc:
        print(f"FAIL: Connected but query failed: {exc}")
        return 1
    finally:
        dispose_engine()

    print("OK: Connection successful.")
    print(f"MySQL version: {version_row}")
    print(f"Current database: {db_row}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
