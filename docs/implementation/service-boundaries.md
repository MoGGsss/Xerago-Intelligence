# Service Boundaries (MVP)

## Overview

Four logical services, three long-running **Python** processes, one async worker pool. Communication across internal boundaries is **async** via Redis/Celery—never synchronous HTTP between ingest and processing.

**Integration boundary (post-MVP):** the company **Next.js + React + TypeScript** application calls the **FastAPI** read API over HTTPS. It does not participate in ingestion or processing.

```
                    ┌─────────────────┐
                    │    FreshRSS     │
                    │  (RSS state)    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  ingest-bridge  │  Python
                    └────────┬────────┘
                             │ artifact.ingested
                    ┌────────▼────────┐
                    │  Redis / Celery │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
┌────────▼────────┐ ┌────────▼────────┐ ┌───────▼───────┐
│ process_artifact│ │     enrich      │ │     score     │  Python worker
│  (Celery task)  │ │  (Celery task)  │ │ (Celery task) │
└────────┬────────┘ └────────┬────────┘ └───────┬───────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                    ┌────────▼────────┐
                    │     MySQL       │
                    │  (intelligence) │
                    └────────┬────────┘
                             │ SELECT only
                    ┌────────▼────────┐
                    │   FastAPI API   │  Python
                    └────────┬────────┘
                             │ GET /v1/intelligence (HTTPS)
                    ┌────────▼────────┐
                    │  Next.js app    │  TypeScript (company platform, post-MVP)
                    │  React UI       │
                    └─────────────────┘
```

---

## Boundary Summary

| Boundary | Technology | Direction |
|----------|------------|-----------|
| FreshRSS → ingest | HTTP (Reader API) | Pull |
| ingest → queue | Redis / Celery | Event |
| worker → MySQL | SQLAlchemy | Read/write pipeline tables |
| api → MySQL | SQLAlchemy | **Read-only** |
| Next.js → api | HTTP REST + JSON | **Read-only** |
| worker → LLM | HTTP (Ollama / company API) | Request/response |

**No boundary** between Next.js and MySQL, Redis, FreshRSS, Celery, or LLM.

---

## Service 1: Ingest Bridge (`services/ingest`) — Python

### Responsibility

- Poll FreshRSS for new entries since last cursor per `source_id`
- Poll GitHub Releases API for `registry/repos.yaml` entries
- Normalize to **artifact** rows in MySQL
- Emit **`artifact.ingested`** events
- Update **source_health**

### Does NOT

- Call LLM
- Classify or score
- Serve Next.js or public UI traffic

### Outputs

| Output | Sink |
|--------|------|
| `artifacts` row | MySQL |
| `artifact.ingested` | Redis / Celery |
| `source_health` upsert | MySQL |

### Failure Mode

- FreshRSS down → retry; entries retained in FreshRSS
- GitHub rate limit → ETag, backoff
- MySQL down → **do not advance ingest cursor** until write succeeds

---

## Service 2: Processing Worker (`services/worker`) — Python

### Responsibility

Idempotent Celery tasks: process → enrich → score → publish.

### Task Chain (Happy Path)

```
artifact.ingested
  → task_process_artifact
  → task_enrich              # LLM: summary + why_it_matters
  → task_score
  → task_publish               # status=published in MySQL
```

### Does NOT

- Expose HTTP to browsers or Next.js
- Poll FreshRSS

### Failure Mode

| Failure | Behavior |
|---------|----------|
| LLM error | `status=processing`, retry; artifact preserved in MySQL |
| Dedupe match | Cluster attach; non-canonical suppressed |
| Task retry | Idempotency via `pipeline_runs.idempotency_key` |

---

## Service 3: Strategic Scoring (logical module in worker) — Python

`shared/scoring/` — not a separate deployable. Writes `strategic_score`, `impact_level`, `score_breakdown` to MySQL.

---

## Service 4: API (`services/api`) — Python / FastAPI

### Responsibility

- **Read-only** REST per `docs/output_schema.md`
- JSON responses consumed by **Next.js** (future) and MVP tools (curl, Postman)
- Health: MySQL, Redis, FreshRSS lag
- **CORS** for allowed Next.js origins (`CORS_ORIGINS` env)

### Does NOT

- Enqueue Celery tasks
- Call LLM
- Execute business logic on GET (no precompute on request)
- Run TypeScript or render React

### Endpoints (MVP)

| Method | Path | Consumer |
|--------|------|----------|
| GET | `/v1/intelligence` | Next.js list view (future), internal tools |
| GET | `/v1/intelligence/{id}` | Next.js detail view (future) |
| GET | `/v1/health` | Ops, compose healthcheck |
| GET | `/openapi.json` | Type generation in company repo |

### Failure Mode

- Single MySQL instance — no replica lag concern for MVP
- Unpublished or processing id → 404
- Upstream unavailable → 503 on `/v1/health` only; feed returns last published data

---

## Service 5: Presentation (out of scope — company platform) — Next.js + TypeScript

Not implemented in the intelligence-engine repo during MVP.

### Responsibility (at integration)

- Render intelligence feed and detail UI inside existing company web app
- Server-side `fetch` to FastAPI base URL (avoid exposing internal host to browser when using BFF pattern)
- Map JSON to React components; optional client-side filters

### Does NOT

- Write intelligence rows
- Trigger processing or LLM
- Connect to MySQL directly

### Recommended integration patterns

| Pattern | When |
|---------|------|
| **Server Component fetch** | Default — API URL server-only env `INTELLIGENCE_API_URL` |
| **Next.js Route Handler BFF** | When hiding API key or shaping responses |
| **Client fetch** | Only for interactive filters; still read-only |

Generate TypeScript types from FastAPI OpenAPI in the **company** repository, not in the Python repo.

---

## Event Contract

Unchanged — internal Python pipeline only. Next.js does not subscribe to Redis events in MVP.

### `artifact.ingested`

```json
{
  "event_type": "artifact.ingested",
  "event_id": "evt_ulid",
  "emitted_at": "ISO8601",
  "artifact_id": "uuid",
  "source_id": "sf-blog",
  "content_type": "article | github_release"
}
```

---

## Data Ownership

| Data | Owner | Readers |
|------|-------|---------|
| RSS read state | FreshRSS | ingest (Python) |
| Raw artifacts | MySQL `artifacts` | worker (Python) |
| Clusters, ledger | MySQL | worker (Python) |
| Intelligence records | MySQL | api (Python), worker (publish) |
| Queue messages | Redis | worker (Python) |
| LLM audit | MySQL `enrichment_runs` | worker (Python) |
| Rendered UI state | Next.js app | Browser |

---

## LLM Abstraction Boundary (Python only)

```
enrichment/
  ├── base.py
  ├── ollama.py
  └── company_api.py
```

`LLM_PROVIDER=ollama|company` — worker only.

---

## Security Boundaries

| Secret | Used by |
|--------|---------|
| `FRESHRSS_API_PASSWORD` | ingest |
| `GITHUB_TOKEN` | ingest |
| `DATABASE_URL` (MySQL) | ingest, worker, api |
| `LLM_API_KEY` | worker |
| `INTELLIGENCE_API_KEY` (optional) | api middleware; validated from Next.js BFF |

FastAPI has **no** GitHub or LLM credentials. Next.js has **no** MySQL credentials.

---

## MySQL-Specific Notes

| Topic | Approach |
|-------|----------|
| Charset | `utf8mb4` / `utf8mb4_unicode_ci` on all tables |
| UUIDs | `CHAR(36)` generated in Python (`uuid4`) |
| Timestamps | `DATETIME(6)` stored as UTC |
| JSON columns | MySQL `JSON` type for `score_breakdown`, `promotion_trace`, etc. |
| Migrations | Alembic with `mysql` dialect |
| Connection pool | SQLAlchemy pool per process; api uses read-optimized pool sizing |

---

## Observability (MVP Minimum)

Structured JSON logs in Python services: `artifact_id`, `intelligence_id`, `source_id`.

Next.js integration adds frontend error boundaries only — no pipeline metrics in TS for MVP.

---

## Related

- [project-structure.md](project-structure.md)
- [mvp-implementation-order.md](mvp-implementation-order.md)
