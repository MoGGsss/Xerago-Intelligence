#!/usr/bin/env python3
"""
Temporary diagnostic — test Ollama json_mode with configured model (gpt-oss:20b).

Does not use enrichment code. Uses OllamaClient + settings from .env.

Usage (from backend/):
    python scripts/test_ollama.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_SRC = _BACKEND_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from xerago_intelligence.ai.client import create_ai_client
from xerago_intelligence.config import get_settings


def _run_case(label: str, prompt: str, json_mode: bool) -> int:
    print(f"\n{'=' * 56}", flush=True)
    print(label, flush=True)
    print(f"  json_mode: {json_mode}", flush=True)
    print(f"  prompt:    {prompt!r}", flush=True)
    print("=" * 56, flush=True)

    client = create_ai_client()
    try:
        # OllamaClient.generate() prints Raw HTTP JSON and Mapped text.
        result = client.generate(prompt, json_mode=json_mode)
    except Exception as exc:
        print(f"ERROR: {exc}", flush=True)
        return 1

    print(f"Mapped Text: {result.text}", flush=True)
    print(f"Length:      {len(result.text)}", flush=True)
    return 0


def main() -> int:
    settings = get_settings()
    print("Ollama JSON mode diagnostic", flush=True)
    print(f"  OLLAMA_BASE_URL: {settings.ollama_base_url}", flush=True)
    print(f"  OLLAMA_MODEL:    {settings.ollama_model}", flush=True)
    print(f"  LLM_PROVIDER:    {settings.llm_provider}", flush=True)

    failures = 0
    failures += _run_case(
        "Request A (plain text, json_mode=False)",
        "Return exactly the text HELLO",
        json_mode=False,
    )
    failures += _run_case(
        'Request B (JSON, json_mode=True)',
        'Return exactly {"test":"ok"}',
        json_mode=True,
    )

    print(f"\n{'=' * 56}", flush=True)
    if failures:
        print(f"DONE — {failures} request(s) failed", flush=True)
        return 1
    print(
        "DONE — compare Request A vs B Raw HTTP JSON and Mapped text above.",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
