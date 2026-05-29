# Backend — Xerago Intelligence Engine

Python processing engine (Sprint 1): configuration, MySQL connectivity, and registry loading.

## Structure

```
backend/
├── .env.example
├── requirements.txt
├── README.md
├── scripts/
│   ├── verify_sprint1.py      # Sprint 1 — registry + MySQL
│   └── verify_mysql.py        # Sprint 0.5 — MySQL only
└── src/
    └── xerago_intelligence/
        ├── config/
        │   └── settings.py    # pydantic-settings
        ├── db/
        │   └── connection.py  # SQLAlchemy + PyMySQL
        └── registry/
            ├── models.py      # Pydantic models for YAML
            └── loader.py      # load sources.yaml & repos.yaml
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

## Verify Sprint 1

Run from the `backend/` directory:

```powershell
python scripts\verify_sprint1.py
```

Expected:

```
SUCCESS — registry loaded and MySQL connected.
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
