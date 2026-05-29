#!/usr/bin/env python3
"""Sprint 1 verification: registry load + MySQL connectivity."""

from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import quote_plus, urlparse

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_SRC = _BACKEND_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from xerago_intelligence.config import get_settings
from xerago_intelligence.db import dispose_engine, probe_connection
from xerago_intelligence.registry import RegistryError, load_registry


def _mask_database_url(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.hostname or ""
    port = parsed.port or ""
    user = parsed.username or ""
    db = (parsed.path or "").lstrip("/")
    return f"mysql+pymysql://{user}:***@{host}:{port}/{db}"


def main() -> int:
    print("Xerago Intelligence Engine — Sprint 1 verification")
    print("=" * 56)

    settings = get_settings()
    failures = 0

    # --- Registry ---
    print("\n[1/2] Registry")
    try:
        bundle = load_registry(settings=settings)
        print(f"  Project root: {bundle.project_root}")
        print(f"  Sources file: {settings.sources_yaml_path}")
        print(f"  Repos file:   {settings.repos_yaml_path}")
        print(f"  Sources version: {bundle.sources.version}")
        print(f"  Entities: {len(bundle.sources.entities)}")
        print(f"  Sources:  {len(bundle.sources.sources)} "
              f"({bundle.enabled_source_count} enabled)")
        print(f"  Repos version:   {bundle.repos.version}")
        print(f"  Repositories:    {len(bundle.repos.repositories)} "
              f"({bundle.enabled_repo_count} enabled, "
              f"{bundle.mvp_repo_count} mvp)")
        print("  Registry: OK")
    except (RegistryError, FileNotFoundError, ValueError) as exc:
        print(f"  Registry: FAIL — {exc}")
        failures += 1

    # --- MySQL ---
    print("\n[2/2] MySQL")
    settings.log_mysql_startup()
    url = settings.resolved_database_url()
    print(f"  URL (masked): {_mask_database_url(url)}")
    result = probe_connection()
    if result.ok:
        print("  Connection: OK")
        print(f"  MySQL version: {result.mysql_version}")
        print(f"  Database:      {result.current_database}")
    else:
        print(f"  Connection: FAIL — {result.error}")
        if settings.mysql_user != "root":
            print("  Hint: set MYSQL_USER=root in backend/.env")
        if settings.database_url:
            print(
                "  Hint: DATABASE_URL overrides MYSQL_* — "
                "comment it out in .env to use discrete variables"
            )
        failures += 1

    dispose_engine()

    print("\n" + "=" * 56)
    if failures:
        print(f"FAILED ({failures} check(s))")
        return 1
    print("SUCCESS — registry loaded and MySQL connected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
