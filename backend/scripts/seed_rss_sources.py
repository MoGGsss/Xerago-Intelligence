#!/usr/bin/env python3
"""Seed Phase 8 RSS sources into rss_sources table."""

from __future__ import annotations

import sys
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_SRC = _BACKEND_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


def main() -> int:
    from xerago_intelligence.config import get_settings
    from xerago_intelligence.db import dispose_engine, session_scope
    from xerago_intelligence.db.connection import probe_connection
    from xerago_intelligence.db.repositories.rss_source_repository import RssSourceRepository

    settings = get_settings()
    settings.log_mysql_startup()
    if not probe_connection().ok:
        print("FAIL: Cannot connect to MySQL.")
        return 1

    with session_scope() as session:
        repo = RssSourceRepository(session)
        count = repo.seed_phase8_catalog()
        session.commit()
        active = len(repo.list_active())
        print(f"OK: Seeded/updated {count} RSS sources ({active} active).")

    dispose_engine()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
