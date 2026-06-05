# Department Intelligence Mapping

## Purpose

Maps enriched intelligence artifacts to **Xerago company departments** with relevance scores. Orthogonal to strategic scoring (`strategic_score`); consumes stored enrichment output only.

Version: `dept_map_v2.0.0` (Phase 1A consolidation)

---

## Departments (10)

AI Engineering · Solutions · Digital Analytics · Strategy, Design & Innovation · Digital Operations · Sales · Account Management · Content & Digital Marketing · MarTech & Campaign Services · Xerago Securities

Legacy names and slugs (23-department registry) remain valid for **90 days** via alias resolution — see `DEPARTMENT_SLUG_ALIASES` / `DEPARTMENT_NAME_ALIASES` in `backend/src/xerago_intelligence/taxonomy/departments.py`.

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
5. **Selection** — include scores ≥ 40; cap at 5; fallback to Strategy, Design & Innovation (including `industry-trends`).

---

## Pipeline

```
enrich_artifact() → StrategicScorer (unchanged) → DepartmentMappingService.map_artifact()
```

Backfill mappings: `python scripts/backfill_department_mappings.py` (`--force` to remap all).

Consolidate legacy DB rows to 10 departments: `python scripts/backfill_department_consolidation.py`.

---

## API

`IntelligenceItem` includes:

- `departments[]` — `{ department_name, department_relevance_score }`
- `department` — primary (highest score); deprecated alias

Filter: `GET /intelligence?department=MarTech` resolves to MarTech & Campaign Services (alias).

---

## Related

- `docs/department_consolidation_phase1a_report.md` — migration impact
- `docs/categories.md` — domain/signal taxonomy (mapping inputs)
- `backend/src/xerago_intelligence/taxonomy/` — registry and rules
