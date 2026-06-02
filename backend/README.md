# Backend — Xerago Intelligence Engine

Python processing engine: configuration, MySQL, registry loading, RSS ingestion (2A/2B), LLM enrichment (3A).

## Structure

```
backend/
├── .env.example
├── requirements.txt
├── README.md
├── db/schema/
│   ├── artifacts.sql
│   ├── ingest_cursors.sql
│   └── artifact_enrichments.sql
├── scripts/
│   ├── verify_sprint3b.py     # Sprint 3B — classification validation
│   ├── verify_sprint3a.py     # Sprint 3A — Ollama enrichment
│   ├── verify_sprint2b.py     # Sprint 2B — incremental RSS
│   ├── verify_sprint2a.py     # Sprint 2A — RSS → MySQL
│   ├── apply_schema.py
│   ├── verify_sprint1.py      # Sprint 1 — registry + MySQL
│   └── verify_mysql.py        # Sprint 0.5 — MySQL only
└── src/
    └── xerago_intelligence/
        ├── config/
        │   └── settings.py    # pydantic-settings
        ├── db/
        │   └── connection.py  # SQLAlchemy + PyMySQL
        ├── db/
        │   ├── models/artifact.py
        │   └── repositories/artifact_repository.py
        ├── ai/
        │   ├── client.py
        │   └── providers/ollama.py
        ├── enrichment/service.py
        ├── ingest/rss.py
        ├── registry/
        │   ├── models.py
        │   └── loader.py
        └── utils/url.py
```

Registry files live at the **repository root**: `../registry/sources.yaml`, `../registry/repos.yaml`.

## Prerequisites

- Python 3.11+ (3.14 supported)
- MySQL 8 with database `xerago_intelligence`

## Setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Edit .env with your MySQL credentials
```

## Run FastAPI (Sprint 5)

```powershell
pip install -r requirements.txt
cd backend
$env:PYTHONPATH = "src"
python -m uvicorn xerago_intelligence.api.main:app --host 127.0.0.1 --port 8000
```

Endpoints: `GET /health`, `GET /v1/intelligence`, `GET /v1/intelligence/top`, `GET /v1/intelligence/{artifact_id}`

## Verify Sprint 5 (FastAPI read API)

```powershell
pip install -r requirements.txt
python scripts\verify_sprint5.py
```

## Verify Sprint 4 (strategic scoring)

Requires a validated enrichment row (Sprint 3A/3B):

```powershell
python scripts\apply_schema.py
python scripts\verify_sprint4.py
```

## Verify Sprint 3B (classification validation)

Requires an existing `artifact_enrichments` row (run Sprint 3A first):

```powershell
python scripts\apply_schema.py
python scripts\verify_sprint3b.py
```

## Verify Sprint 3A (LLM enrichment)

Set Ollama in `.env` (see `.env.example`), then:

```powershell
python scripts\apply_schema.py
python scripts\verify_sprint3a.py
```

Requires network access to `OLLAMA_BASE_URL` and model `gpt-oss:20b`.

## Verify Sprint 2B (incremental RSS)

```powershell
python scripts\apply_schema.py
python scripts\verify_sprint2b.py
```

Second run should show `processed=0`, `inserted=0`, and `skipped_cursor` equal to feed size.

## Verify Sprint 2A (RSS → artifacts)

```powershell
pip install -r requirements.txt
python scripts\verify_sprint2a.py
```

Expected:

```
SUCCESS — RSS articles ingested and stored in artifacts table.
```

## Verify Sprint 1

```powershell
python scripts\verify_sprint1.py
```

## Configuration

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Full `mysql+pymysql://...` URL — **overrides `MYSQL_*` when set** |
| `MYSQL_USER` | Default `root` for local dev |
| `MYSQL_*` | Discrete connection settings (used when `DATABASE_URL` is unset) |
| `PROJECT_ROOT` | Path to repo root (auto-detected if omitted) |
| `DB_ECHO` | SQLAlchemy SQL logging |

## Programmatic usage

```python
from xerago_intelligence.config import get_settings
from xerago_intelligence.db import check_connection
from xerago_intelligence.registry import load_registry

bundle = load_registry()
assert check_connection()
print(bundle.sources.version, len(bundle.sources.sources))
```
