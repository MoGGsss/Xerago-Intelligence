#!/usr/bin/env python3
"""One-off RSS feed quality audit for Phase 8 catalog."""

from __future__ import annotations

import sys
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_SRC = _BACKEND_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import feedparser  # noqa: E402
import requests  # noqa: E402

from xerago_intelligence.ingest.feed_fetch import FeedFetchConfig, create_http_session  # noqa: E402
from xerago_intelligence.ingest.source_catalog import PHASE_8_RSS_SOURCES  # noqa: E402


def main() -> int:
    config = FeedFetchConfig()
    session = create_http_session(config)
    results: list[dict] = []

    for seed in PHASE_8_RSS_SOURCES:
        row: dict = {
            "source_id": seed.source_id,
            "source_name": seed.source_name,
            "rss_url": seed.rss_url,
            "status": "",
            "http_status": None,
            "redirects": [],
            "final_url": "",
            "entries": 0,
            "content_type": "",
            "error": "",
            "classification": "",
        }
        try:
            resp = session.get(seed.rss_url, timeout=30, allow_redirects=True)
            row["http_status"] = resp.status_code
            row["final_url"] = resp.url
            row["content_type"] = resp.headers.get("Content-Type", "")
            if resp.history:
                row["redirects"] = [(r.status_code, r.url) for r in resp.history]

            if resp.status_code in (401, 403):
                row["classification"] = "auth_required"
                row["status"] = "auth_required"
            elif resp.status_code >= 400:
                row["classification"] = "broken"
                row["status"] = f"HTTP {resp.status_code}"
            else:
                parsed = feedparser.parse(resp.content)
                row["entries"] = len(parsed.entries)
                if parsed.bozo and not parsed.entries:
                    row["classification"] = "broken"
                    row["status"] = f"parse_error: {parsed.bozo_exception}"
                elif row["entries"] == 0:
                    row["classification"] = "empty"
                    row["status"] = "empty_feed"
                else:
                    row["classification"] = "valid"
                    row["status"] = "valid"
                    if parsed.bozo:
                        row["error"] = str(parsed.bozo_exception)
        except requests.exceptions.SSLError as exc:
            row["classification"] = "broken"
            row["status"] = f"SSL error: {exc}"
        except requests.exceptions.Timeout:
            row["classification"] = "broken"
            row["status"] = "timeout"
        except requests.exceptions.ConnectionError as exc:
            row["classification"] = "broken"
            row["status"] = f"connection_error: {exc}"
        except Exception as exc:
            row["classification"] = "broken"
            row["status"] = str(exc)

        if row["redirects"] and row["classification"] == "valid":
            row["status"] = "valid (redirect)"
        elif row["redirects"] and row["classification"] != "valid":
            row["status"] += " (redirect)"

        results.append(row)

    session.close()

    print(f"{'Source':<22} {'Class':<14} {'HTTP':<5} {'Entries':<8} {'Redir':<6} Status")
    print("-" * 100)
    for row in results:
        redir = "yes" if row["redirects"] else "no"
        http = row["http_status"] if row["http_status"] is not None else "N/A"
        print(
            f"{row['source_name']:<22} {row['classification']:<14} {http!s:<5} "
            f"{row['entries']:<8} {redir:<6} {row['status']}"
        )
        if row["redirects"]:
            for code, url in row["redirects"]:
                print(f"  -> {code} {url}")
        if row["final_url"] and row["final_url"] != row["rss_url"]:
            print(f"  final: {row['final_url']}")
        if row["error"]:
            print(f"  warn: {row['error']}")

    print()
    print("SUMMARY:")
    for cls in ("valid", "empty", "auth_required", "broken"):
        items = [r["source_name"] for r in results if r["classification"] == cls]
        print(f"  {cls}: {len(items)} - {items}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
