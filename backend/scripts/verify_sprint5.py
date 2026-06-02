#!/usr/bin/env python3
"""Sprint 5 verification: FastAPI read-only intelligence API."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

import requests

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_SRC = _BACKEND_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

API_HOST = "127.0.0.1"
API_PORT = 8765
BASE_URL = f"http://{API_HOST}:{API_PORT}"

REQUIRED_ITEM_FIELDS = {
    "artifact_id",
    "title",
    "url",
    "published_at",
    "summary",
    "why_it_matters",
    "domain",
    "signal_type",
    "confidence_score",
    "validation_status",
    "strategic_score",
    "priority_level",
}


def _wait_for_health(timeout_seconds: float = 30.0) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(0.5)
    return False


def _validate_item(item: dict, label: str) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED_ITEM_FIELDS - set(item.keys())
    if missing:
        errors.append(f"{label}: missing fields {sorted(missing)}")
    for field in ("artifact_id", "title", "url", "summary", "domain"):
        if field in item and not item[field]:
            errors.append(f"{label}: empty {field}")
    return errors


def main() -> int:
    failures = 0

    print("Xerago Intelligence Engine — Sprint 5 verification", flush=True)
    print("=" * 56, flush=True)

    print("\n[1/5] Start FastAPI (uvicorn)", flush=True)
    env = dict(**__import__("os").environ)
    env["PYTHONPATH"] = str(_SRC)

    server = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "xerago_intelligence.api.main:app",
            "--host",
            API_HOST,
            "--port",
            str(API_PORT),
        ],
        cwd=str(_BACKEND_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        if not _wait_for_health():
            print("  FAIL: API did not become healthy in time.", flush=True)
            if server.stdout:
                print(server.stdout.read() or "", flush=True)
            return 1
        print(f"  API running at {BASE_URL}", flush=True)

        print("\n[2/5] GET /health", flush=True)
        health = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"  status: {health.status_code}", flush=True)
        if health.status_code != 200:
            print("  FAIL: /health", flush=True)
            failures += 1
        else:
            body = health.json()
            print(f"  body: {json.dumps(body)}", flush=True)
            if body.get("status") != "ok":
                print("  FAIL: health status not ok", flush=True)
                failures += 1

        print("\n[3/5] GET /v1/intelligence", flush=True)
        listing = requests.get(
            f"{BASE_URL}/v1/intelligence",
            params={"page": 1, "page_size": 20},
            timeout=15,
        )
        print(f"  status: {listing.status_code}", flush=True)
        if listing.status_code != 200:
            print("  FAIL: /v1/intelligence", flush=True)
            failures += 1
        else:
            data = listing.json()
            for key in ("items", "page", "page_size", "total"):
                if key not in data:
                    print(f"  FAIL: missing list key {key!r}", flush=True)
                    failures += 1
            print(
                f"  total={data.get('total')} items={len(data.get('items', []))}",
                flush=True,
            )
            if data.get("items"):
                failures += len(_validate_item(data["items"][0], "list[0]"))
            else:
                print("  WARN: no intelligence items in database", flush=True)

        print("\n[4/5] GET /v1/intelligence/top", flush=True)
        top = requests.get(f"{BASE_URL}/v1/intelligence/top", timeout=15)
        print(f"  status: {top.status_code}", flush=True)
        if top.status_code != 200:
            print("  FAIL: /v1/intelligence/top", flush=True)
            failures += 1
        else:
            top_items = top.json()
            if not isinstance(top_items, list):
                print("  FAIL: /top response is not a list", flush=True)
                failures += 1
            else:
                print(f"  top count: {len(top_items)}", flush=True)
                if top_items:
                    failures += len(_validate_item(top_items[0], "top[0]"))
                    print(
                        f"  top[0] priority={top_items[0].get('priority_level')} "
                        f"score={top_items[0].get('strategic_score')}",
                        flush=True,
                    )

        print("\n[5/5] GET /v1/intelligence/{{artifact_id}}", flush=True)
        artifact_id = None
        if listing.status_code == 200 and listing.json().get("items"):
            artifact_id = listing.json()["items"][0]["artifact_id"]
        elif top.status_code == 200 and top.json():
            artifact_id = top.json()[0]["artifact_id"]

        if artifact_id:
            detail = requests.get(
                f"{BASE_URL}/v1/intelligence/{artifact_id}",
                timeout=15,
            )
            print(f"  status: {detail.status_code}", flush=True)
            if detail.status_code != 200:
                print("  FAIL: detail endpoint", flush=True)
                failures += 1
            else:
                failures += len(_validate_item(detail.json(), "detail"))
                print(f"  artifact_id: {artifact_id}", flush=True)
        else:
            print("  SKIP: no artifact_id available for detail test", flush=True)

    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()

    print("\n" + "=" * 56, flush=True)
    if failures:
        print(f"FAILED ({failures} check(s))", flush=True)
        return 1
    print(
        "SUCCESS — FastAPI serves intelligence records with enrichment and scoring.",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
