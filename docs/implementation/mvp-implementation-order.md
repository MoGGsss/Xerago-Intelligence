# MVP Implementation Order

## Guiding Rules

1. **Vertical slices** — Each sprint delivers a testable slice of the north-star pipeline, not a layer in isolation.
2. **No big-bang** — Do not implement all services before first artifact flows end-to-end.
3. **Rules before LLM** — Classification, dedup, and gates work without LLM; add enrichment once artifacts are stable.
4. **Read API last among features** — But scaffold DB + migrations in Sprint 1.
5. **Wave 1 sources only** until pipeline proven (`mvp_wave: 1` in `registry/sources.yaml`).

---

## Sprint Map (8 Sprints × ~1 week)

| Sprint | Theme | Pipeline stage unlocked |
|--------|-------|-------------------------|
| **S0** | Scaffold & infra | — |
| **S1** | DB + registry loader | Persist artifacts |
| **S2** | Ingest (FreshRSS) | Article → MySQL (raw) |
| **S3** | Process + gate (no LLM) | Filtered candidate rows |
| **S4** | Enrichment (LLM) | Summary + Why It Matters |
| **S5** | Scoring + publish | Strategic score → published |
| **S6** | REST API | Read intelligence |
| **S7** | GitHub OSS + hardening | OSS lifecycle + MVP sign-off |

---

## Sprint 0 — Scaffold & Local Infra

**Goal:** `docker compose up` brings MySQL, Redis, FreshRSS online.

### Deliverables

- [ ] `deploy/docker-compose.yml` + `deploy/.env.example`
- [ ] Folder skeleton per [project-structure.md](project-structure.md) (empty packages + `.gitkeep`)
- [ ] `Makefile`: `make up`, `make down`, `make logs`
- [ ] `services/shared/pyproject.toml` with dev deps (ruff, pytest)
- [ ] README quickstart (5 commands to running stack)

### Exit

- FreshRSS UI reachable; MySQL accepts connections (`utf8mb4`)
- No application logic required

### Do not start

- Celery tasks, FastAPI routes, LLM integration

---

## Sprint 1 — Database & Shared Kernel

**Goal:** Migrations apply; registry loads; repositories can CRUD artifacts.

### Deliverables

- [ ] Apply `db/schema/001_initial.sql` via Alembic baseline
- [ ] SQLAlchemy models matching schema (`shared/models/`)
- [ ] `registry/loader.py` — load & validate `sources.yaml`, `repos.yaml`
- [ ] `scripts/load_registry.py` — CLI validation
- [ ] Repository: `ArtifactRepository`, `SourceHealthRepository`
- [ ] Unit tests: registry load, artifact insert

### Exit

- `pytest tests/unit` green for registry + DB repos (Testcontainers or local compose)

### Dependencies

- S0 complete

---

## Sprint 2 — Ingest Bridge (FreshRSS)

**Goal:** New RSS entries become `artifacts` rows and Redis events.

### Deliverables

- [ ] FreshRSS Google Reader API client (`ingest/freshrss/`)
- [ ] Cursor per `source_id` in `ingest_cursors` table
- [ ] `scripts/seed_freshrss_feeds.py` for Wave 1 feeds
- [ ] Normalize entry → `artifacts` (title, url, body_text, published_at, content_hash)
- [ ] Emit `artifact.ingested` to Redis/Celery
- [ ] Update `source_health`
- [ ] Ingest process: `python -m ingest.main` (loop or cron)

### Wave 1 sources

`adobe-blog`, `sf-blog`, `ibm-newsroom`, `openai-blog`, `anthropic-news` (adjust per registry `mvp_wave: 1`)

### Exit

- Manual test: subscribe test feed → artifact row within 2 min
- Re-run ingest → no duplicate artifacts (unique `canonical_url` + hash)

### Do not start

- LLM, scoring, public API

---

## Sprint 3 — Processing Pipeline (Rules Only)

**Goal:** `artifact.ingested` → classified, deduped, gated candidate → `intelligence` row in `processing` / `suppressed`.

### Deliverables

- [ ] Celery app + `task_process_artifact`
- [ ] `rules/eligibility.py` — ELIG-* rules
- [ ] `rules/classify.py` — CLS-* rules (keyword/rules-first)
- [ ] `rules/domains.py` — registry defaults + keyword map
- [ ] `rules/dedupe.py` — URL hash + title fuzzy + clusters
- [ ] `rules/gates.py` — SURF-* (except score threshold uses placeholder 0)
- [ ] Tables: `clusters`, `cluster_members`, `intelligence` (status `processing` or `suppressed`)
- [ ] `promotion_trace` JSON populated

### Exit

- Fixture artifact: marketing fluff → `suppressed`
- Fixture artifact: partner GA release → `processing` + event_type set
- Duplicate URL → single cluster, one canonical

### Do not start

- LLM calls (use stub title as summary for manual DB inspection if needed)

---

## Sprint 4 — Enrichment (LLM)

**Goal:** Gate-passed intelligence rows receive `summary` and `why_it_matters`.

### Deliverables

- [ ] `enrichment/base.py` + `ollama.py` + `company_api.py`
- [ ] Prompt templates (versioned files in `shared/enrichment/prompts/`)
- [ ] `task_enrich` with retry, `enrichment_runs` audit rows
- [ ] Token/length limits per `output_schema.md`
- [ ] Integration test with Ollama (skipped in CI if no GPU)

### Exit

- Published-path record has non-empty summary and why_it_matters
- LLM failure leaves `status=processing`, artifact intact, Celery retries

### Dependencies

- S3 produces `processing` candidates

---

## Sprint 5 — Scoring & Publish

**Goal:** Complete north-star fields; `status=published` for feed-ready rows.

### Deliverables

- [ ] `scoring/engine.py` — `scoring_v2.0.0` factors → `strategic_score` 0–100
- [ ] `impact_level`, `employee_relevance` derivation
- [ ] `intelligence_domains` junction populated
- [ ] `task_score` + `task_publish`
- [ ] Apply `SURF-003` min score 55 — below → `suppressed`
- [ ] `score_breakdown` JSON

### Exit

- End-to-end: RSS article → published intelligence with score ≥ 55 (for high-signal fixtures)
- `task_publish` idempotent (re-run does not duplicate)

---

## Sprint 6 — FastAPI (Read-Only)

**Goal:** External consumers read precomputed intelligence.

### Deliverables

- [ ] FastAPI app + `GET /v1/intelligence`, `GET /v1/intelligence/{id}`
- [ ] `GET /v1/health` — DB, Redis, ingest lag from `source_health`
- [ ] Response schemas mirroring `output_schema.md`
- [ ] Pagination (`limit`, `cursor`), filters (`min_score`, `domain`, `entity`, `since`)
- [ ] `openapi/intelligence-v1.yaml` sync (for Next.js typegen in company repo)
- [ ] CORS configured for Next.js dev origin (`CORS_ORIGINS`)
- [ ] Integration tests: API returns only `published`

### Exit

- Postman/curl: list feed returns enriched records
- GET by id returns `promotion_trace`, `score_breakdown`
- **Verify:** no LLM import in `api` package (lint rule or test)

### Do not start

- Write endpoints, auth (optional API key stub only if needed)

---

## Sprint 7 — GitHub OSS & MVP Hardening

**Goal:** OSS lifecycle works; Wave 2 sources; operational confidence.

### Deliverables

- [ ] GitHub release poller in `ingest/github/`
- [ ] `repository_version_ledger` + `repository_poll_state` enforcement (OSS-001)
- [ ] MVP repos with `mvp: true` in `repos.yaml`
- [ ] Wave 2 RSS sources enabled
- [ ] `scripts/replay_artifact.py`, `scripts/export_calibration.py`
- [ ] Dead letter / `pipeline_runs` failure visibility
- [ ] MVP acceptance tests from PRD §14

### Exit

- LangGraph v1.0 → signal; re-poll v1.0 → no new signal; v1.1 → new signal
- 48h soak: ≥95% enrich success, precision@10 sample ≥0.75 (manual labels)

---

## Critical Path Diagram

```
S0 infra
  → S1 DB + shared
    → S2 ingest
      → S3 rules pipeline
        → S4 LLM enrich
          → S5 score + publish
            → S6 API
              → S7 OSS + harden
```

**Parallelizable after S2:** OpenAPI spec drafting (S6 prep) can start during S4–S5.

---

## Definition of Done (MVP)

| Criterion | Verification |
|-----------|--------------|
| Article → published intelligence | Integration test + manual RSS |
| Summary + why_it_matters present | API GET by id |
| strategic_score 0–100 | API field + breakdown |
| MySQL persistence | Row in `intelligence` |
| REST read-only | No side effects on GET |
| Local-first compose | README quickstart on clean machine |
| OSS no re-surface | S7 ledger test |
| No frontend | — |

---

## Risk Mitigation per Sprint

| Sprint | Risk | Mitigation |
|--------|------|------------|
| S2 | FreshRSS API quirks | Start with single test feed; document API version |
| S3 | Over-filtering | Log all `suppressed` reasons; weekly review export |
| S4 | LLM quality | Prompt templates + max length; human review export in S7 |
| S5 | Score miscalibration | `export_calibration.py` + spreadsheet |
| S6 | Schema drift | DTO tests against fixtures from `output_schema.md` |
| S7 | GitHub rate limits | ETag + `GITHUB_TOKEN`; Tier A cadence only |

---

## Post-MVP (Do Not Pull Forward)

- User feedback (`useful` / `not useful`)
- Vector dedup (Qdrant)
- Research store search API
- Slack digest
- Website embed
- TypeScript BFF

---

## Related

- [project-structure.md](project-structure.md)
- [service-boundaries.md](service-boundaries.md)
- [../../db/schema/001_initial.sql](../../db/schema/001_initial.sql)
- [../roadmap.md](../roadmap.md)
