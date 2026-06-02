#!/usr/bin/env python3
"""Sprint 3A verification: enrich a stored artifact via Ollama gpt-oss:20b."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_SRC = _BACKEND_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from xerago_intelligence.config import get_settings
from xerago_intelligence.db import dispose_engine, probe_connection, session_scope
from xerago_intelligence.db.repositories.artifact_repository import ArtifactRepository
from xerago_intelligence.db.repositories.enrichment_repository import EnrichmentRepository
from xerago_intelligence.ai.client import create_ai_client
from xerago_intelligence.enrichment.prompts import build_enrichment_prompt
from xerago_intelligence.enrichment.service import ArtifactEnrichmentService
from xerago_intelligence.ingest.rss import (
    DEFAULT_TEST_SOURCE_ID,
    OPENAI_NEWS_RSS,
    RssIngestionService,
)

SCHEMA_DIR = _BACKEND_ROOT / "db" / "schema"


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )


def _apply_schemas() -> None:
    from sqlalchemy import text

    from xerago_intelligence.db import get_engine

    for path in sorted(SCHEMA_DIR.glob("*.sql")):
        sql = path.read_text(encoding="utf-8")
        statements = [
            s.strip()
            for s in sql.split(";")
            if s.strip() and not s.strip().startswith("--")
        ]
        engine = get_engine()
        with engine.begin() as conn:
            for statement in statements:
                conn.execute(text(statement))


def _ensure_sample_artifact(session) -> str:
    repo = ArtifactRepository(session)
    recent = repo.list_recent(limit=1)
    if recent:
        return recent[0].artifact_id

    print("  No artifacts found — running one RSS ingest...", flush=True)
    service = RssIngestionService(session)
    try:
        result = service.ingest_feed(OPENAI_NEWS_RSS, DEFAULT_TEST_SOURCE_ID)
    finally:
        service.close()
    print(
        f"  Ingest: fetched={result.fetched} inserted={result.inserted}",
        flush=True,
    )
    recent = repo.list_recent(limit=1)
    if not recent:
        raise RuntimeError("No artifact available after ingest.")
    return recent[0].artifact_id


def main() -> int:
    _configure_logging()
    failures = 0

    print("Xerago Intelligence Engine — Sprint 3A verification", flush=True)
    print("=" * 56, flush=True)

    settings = get_settings()

    print("\n[1/5] MySQL", flush=True)
    settings.log_mysql_startup()
    if not probe_connection().ok:
        print("  FAIL: MySQL connection", flush=True)
        return 1
    print("  MySQL: OK", flush=True)

    print("\n[2/5] Ollama configuration", flush=True)
    print(f"  LLM_PROVIDER:     {settings.llm_provider}", flush=True)
    print(f"  OLLAMA_BASE_URL:  {settings.ollama_base_url}", flush=True)
    print(f"  OLLAMA_MODEL:     {settings.ollama_model}", flush=True)

    print("\n[3/5] Schema", flush=True)
    try:
        _apply_schemas()
        print("  Schema: OK", flush=True)
    except Exception as exc:
        print(f"  FAIL: {exc}", flush=True)
        return 1

    print("\n[4/5] Enrich artifact via Ollama", flush=True)
    try:
        with session_scope() as session:
            artifact_id = _ensure_sample_artifact(session)
            artifact = ArtifactRepository(session).get_by_id(artifact_id)
            print(f"  artifact_id: {artifact_id}", flush=True)
            print(f"  title:       {artifact.title[:80] if artifact else '?'}", flush=True)

            enrich_service = ArtifactEnrichmentService(session)
            prompt = build_enrichment_prompt(
                title=artifact.title,
                source_id=artifact.source_id,
                url=artifact.url,
                published_at=artifact.published_at.isoformat(),
                body=artifact.raw_content,
            )
            generate_result = create_ai_client().generate(prompt, json_mode=False)
            print(f"RAW MODEL RESPONSE: {generate_result.text}", flush=True)
            result = enrich_service.enrich_artifact(
                artifact_id,
                force=True,
                precomputed_response=generate_result.text,
            )

        print(f"  created:     {result.created}", flush=True)
        print(f"  domain:      {result.payload.domain}", flush=True)
        print(f"  signal_type: {result.payload.signal_type}", flush=True)
        print(f"  summary:     {result.payload.summary[:120]}…", flush=True)
        print(
            f"  why_it_matters: {result.payload.why_it_matters[:120]}…",
            flush=True,
        )

        if not result.payload.summary or not result.payload.why_it_matters:
            print("  FAIL: Empty summary or why_it_matters", flush=True)
            failures += 1

    except Exception as exc:
        print(f"  FAIL: {exc}", flush=True)
        import traceback

        traceback.print_exc()
        dispose_engine()
        return 1

    print("\n[5/5] Verify artifact_enrichments row", flush=True)
    try:
        with session_scope() as session:
            row = EnrichmentRepository(session).get_by_artifact_id(artifact_id)
            if row is None:
                print("  FAIL: No enrichment row in MySQL.", flush=True)
                failures += 1
            else:
                print(f"  enrichment_id:  {row.enrichment_id}", flush=True)
                print(f"  provider/model: {row.provider} / {row.model}", flush=True)
                print(f"  prompt_version: {row.prompt_version}", flush=True)
                print(f"  enriched_at:    {row.enriched_at}", flush=True)
                if row.model != settings.ollama_model:
                    print(
                        f"  WARN: model {row.model!r} != configured {settings.ollama_model!r}",
                        flush=True,
                    )
    except Exception as exc:
        print(f"  FAIL: {exc}", flush=True)
        failures += 1

    dispose_engine()

    print("\n" + "=" * 56, flush=True)
    if failures:
        print(f"FAILED ({failures} check(s))", flush=True)
        return 1
    print(
        "SUCCESS — artifact enriched with gpt-oss:20b and saved to artifact_enrichments.",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
