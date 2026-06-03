# Department Intelligence Mapping

## Purpose

Maps enriched intelligence artifacts to **Xerago company departments** with relevance scores. Orthogonal to strategic scoring (`strategic_score`); consumes stored enrichment output only.

Version: `dept_map_v1.0.0`

---

## Departments (23)

Account Management, Administration, AI Engineering, Campaign Services, Content, Digital Analytics, Digital Marketing, Digital Operations, Finance & Legal, Founder's Office, HR, IT Operations & Support, MarTech, New Initiatives, Operations, Partner Management, Program Management, QC, Revenue Growth, Sales, Solutions, Strategy & Design, Xerago Securities.

---

## Data Model

Table: `artifact_department_mappings`

| Column | Description |
|--------|-------------|
| `artifact_id` | FK → `artifacts` |
| `department_name` | Canonical display name |
| `department_relevance_score` | 0–100 |
| `mapping_version` | Rule set version |

Constraints: unique `(artifact_id, department_name)`; up to **5** departments per artifact.

---

## Mapping Algorithm

1. **Domain base weights** — primary signal from enrichment `domain`.
2. **Signal boosts** — additive from enrichment `signal_type` (L1).
3. **Keyword boosts** — optional match on `title`, `summary`, `why_it_matters`.
4. **Confidence dampening** — multiply by `confidence_score / 100`.
5. **Selection** — include scores ≥ 40; cap at 5; fallback to Strategy & Design (or Founder's Office for `industry-trends`).

---

## Pipeline

```
enrich_artifact() → StrategicScorer (unchanged) → DepartmentMappingService.map_artifact()
```

Backfill: `python scripts/backfill_department_mappings.py` (`--force` to remap all).

---

## API

`IntelligenceItem` includes:

- `departments[]` — `{ department_name, department_relevance_score }`
- `department` — primary (highest score); deprecated alias

Filter: `GET /intelligence?department=MarTech` or `GET /intelligence/department/MarTech`.

---

## Related

- `docs/categories.md` — domain/signal taxonomy (mapping inputs)
- `backend/src/xerago_intelligence/taxonomy/` — registry and rules
