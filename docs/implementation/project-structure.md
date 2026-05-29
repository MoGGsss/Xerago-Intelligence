# Final Project Folder Structure (MVP)

## Design Intent

- **Monorepo, multi-process** — One repository; separate runnable processes for API, workers, and ingest bridge.
- **Shared kernel** — Domain models, registry loaders, rules, and scoring live in a single Python package to avoid drift.
- **Config as data** — `registry/*.yaml` and `.env` drive behavior; no hardcoded source lists in code.
- **Local-first** — `deploy/docker-compose.yml` runs MySQL, Redis, FreshRSS, Ollama (optional) on a developer machine.
- **Python processing engine** — Ingest, pipeline, enrichment, and scoring remain Python (Celery + FastAPI).
- **Integration target** — Company **Next.js + React + TypeScript** app consumes the intelligence API read-only (post-MVP embed); not built in this repo during MVP.

---

## Runtime Topology

```
┌─────────────────────────────────────────────────────────────┐
│  Company platform (post-MVP integration — separate repo)     │
│  Next.js + React + TypeScript                                │
│  Server Components / Route Handlers → fetch intelligence API │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTPS GET (read-only)
┌────────────────────────────▼────────────────────────────────┐
│  xerago-intelligence-engine (this repo)                      │
│  FastAPI (api) ← MySQL (intelligence) ← worker (Python)     │
│                    ↑ ingest-bridge (Python)                  │
│                    FreshRSS · Redis · GitHub                 │
└─────────────────────────────────────────────────────────────┘
```

MVP validates the **Python backend pipeline** only. Next.js integration is a thin HTTP client layer added to the existing company web app later.

---

## Repository Tree

```
xerago-intelligence-engine/
│
├── docs/                          # Architecture & product (existing)
├── registry/                      # sources.yaml, repos.yaml, schemas (existing)
│
├── deploy/                        # Local runtime — infrastructure only
│   ├── docker-compose.yml         # mysql, redis, freshrss, ollama (profile)
│   ├── .env.example               # DATABASE_URL (mysql+aiomysql / pymysql), etc.
│   └── freshrss/
│       ├── README.md              # Feed import from registry/sources.yaml
│       └── extensions/            # Webhook extension config (if used)
│
├── db/
│   ├── schema/
│   │   └── 001_initial.sql        # MySQL 8.0+ baseline DDL
│   └── migrations/                # Alembic revisions (created in Sprint 1)
│       └── .gitkeep
│
├── openapi/
│   └── intelligence-v1.yaml       # Contract for Next.js type generation (post-MVP)
│
├── services/                      # Deployable processes (Python only)
│   │
│   ├── shared/                    # Library — imported by api, worker, ingest
│   │   ├── pyproject.toml         # Package: xerago_intelligence
│   │   └── src/xerago_intelligence/
│   │       ├── config/
│   │       ├── registry/
│   │       ├── models/            # SQLAlchemy 2.x (MySQL dialect) + Pydantic
│   │       ├── db/                # Session factory, repositories
│   │       ├── pipeline/
│   │       ├── rules/
│   │       ├── scoring/
│   │       ├── enrichment/
│   │       ├── events/
│   │       └── utils/
│   │
│   ├── ingest/                    # Process: ingest-bridge (Python)
│   ├── worker/                    # Process: Celery workers (Python)
│   └── api/                       # Process: FastAPI read-only (Python)
│
├── scripts/
├── tests/
├── Makefile
└── README.md
```

**Not in this repo (MVP):** `apps/web/` Next.js application — lives in the **existing company platform** repository at integration time.

---

## Package Boundaries (Python)

| Package / Process | Role | Stack |
|-------------------|------|-------|
| `xerago_intelligence` (`shared`) | Domain logic | Python, SQLAlchemy (MySQL), pydantic, httpx |
| `ingest` | FreshRSS/GitHub → `artifacts` | Python |
| `worker` | Async pipeline | Python, Celery |
| `api` | REST read layer | Python, FastAPI |

**Rule:** `api` must **not** import enrichment executors or Celery tasks.

**Rule:** No TypeScript runtime in this repo for MVP. TypeScript types for the company app are generated from OpenAPI **against** the FastAPI service (consumer-side).

---

## Configuration Layout

| Location | Purpose |
|----------|---------|
| `deploy/.env` | `DATABASE_URL=mysql+pymysql://user:pass@mysql:3306/xerago_intelligence`, `REDIS_URL`, `FRESHRSS_URL`, `LLM_*`, `CORS_ORIGINS` |
| `registry/sources.yaml` | Source definitions |
| `registry/repos.yaml` | GitHub watchlist |

### DATABASE_URL (MySQL)

Use SQLAlchemy URL form:

- Sync workers: `mysql+pymysql://...`
- FastAPI async (optional): `mysql+aiomysql://...`

Set `charset=utf8mb4` and UTC handling in session config.

---

## Integration Contract (Next.js — Post-MVP)

| Concern | Owner | Notes |
|---------|-------|-------|
| Intelligence UI | Next.js app (company repo) | React components, filters, detail views |
| Data fetch | Next.js Server Components or Route Handlers | `fetch(INTELLIGENCE_API_URL/v1/intelligence)` |
| Types | Generated from OpenAPI | `openapi-typescript` or similar in **consumer** repo |
| Auth | Company platform SSO | API key or JWT gateway in front of FastAPI at integration |
| CORS | FastAPI `api` | Allow Next.js dev/prod origins via `CORS_ORIGINS` |
| Processing | This repo (Python) | Next.js never calls LLM or workers |

Precompute invariant unchanged: Next.js **only reads** `status=published` records.

---

## What We Deliberately Omit (MVP)

| Excluded | Reason |
|----------|--------|
| Next.js / React app in this repo | Integrates into existing company platform later |
| TypeScript API server | FastAPI is the intelligence API |
| RabbitMQ | Redis + Celery sufficient locally |
| `vector/` / Qdrant | Phase 2 |

---

## Docker Compose Services (Local)

| Service | Image / Build | Port |
|---------|---------------|------|
| `mysql` | mysql:8.0 | 3306 |
| `redis` | redis:7-alpine | 6379 |
| `freshrss` | freshrss/freshrss | 8080 |
| `ollama` | ollama/ollama (profile `llm`) | 11434 |
| `api` | build `services/api` | 8000 |
| `worker` | build `services/worker` | — |
| `ingest` | build `services/ingest` | — |

FreshRSS = **RSS state**. MySQL = **intelligence system of record**.

---

## Related

- [service-boundaries.md](service-boundaries.md)
- [mvp-implementation-order.md](mvp-implementation-order.md)
- [../../db/schema/001_initial.sql](../../db/schema/001_initial.sql)
