# Executive Analytics (Phase 10)

## Purpose

Read-only executive dashboard aggregating **existing** intelligence data—no new ingestion or scoring pipelines.

---

## API Design

| Endpoint | Metrics |
|----------|---------|
| `GET /v1/analytics/overview` | Articles today, active sources, enriched count, avg strategic score, feedback totals, last refresh |
| `GET /v1/analytics/departments` | Top departments by opportunity score; department engagement |
| `GET /v1/analytics/opportunities` | Top impact categories; top opportunity types |
| `GET /v1/analytics/sources` | Source contribution (articles, enriched %, avg score) |
| `GET /v1/analytics/feedback` | Positive vs negative, 14-day trends, most useful articles |

### Query parameters

| Param | Endpoints | Default |
|-------|-----------|---------|
| `limit` | departments, opportunities, feedback | 10 |
| `limit` | sources | 20 |
| `days` | feedback | 14 |

### Data sources (tables only)

- `artifact_enrichments` — scores, domains
- `artifact_department_mappings` — departments, categories, types, opportunity scores
- `article_feedback` — usefulness and trends
- `artifacts` — titles, URLs, `source_id`, ingest dates
- `rss_sources` — names, tiers, active flag
- `intelligence_runs` — last refresh timestamp/status

---

## Query Strategy

All analytics run in `AnalyticsRepository` using **SQL `GROUP BY` / `AVG` / `COUNT`**—no per-row Python loops over full tables.

| Query | Pattern | Index use |
|-------|---------|-----------|
| Articles today | `COUNT(*)` on `artifacts.ingested_at >= start_of_day` | `idx_artifacts_published_at` / ingest time |
| Top departments | `AVG(department_opportunity_score)` grouped by `department_name` | department mapping rows |
| Categories / types | `COUNT(*)` on non-null `impact_category` / `opportunity_type` | mapping table |
| Source contribution | `artifacts` LEFT JOIN `artifact_enrichments` GROUP BY `source_id` | `idx_artifacts_source_id` |
| Useful articles | Subquery positive feedback counts JOIN `artifacts` | `article_feedback.artifact_id` |
| Feedback trends | `DATE(created_at)` + `feedback_type` last N days | `article_feedback` indexes |

**Top-N caps** (`limit` query param) keep payloads bounded for UI charts.

---

## Frontend Layout

Route: `/analytics` (auth required)

```
┌─────────────────────────────────────────────────────────┐
│ Header · link back to Intelligence Feed · Refresh      │
├─────────────────────────────────────────────────────────┤
│ KPI row: Articles Today | Active Sources | Avg Score | FB │
├──────────────────────────┬──────────────────────────────┤
│ Department Opportunity   │ Opportunity Categories        │
│ Scores (horizontal bars) │ (vertical bars)               │
├──────────────────────────┼──────────────────────────────┤
│ Opportunity Types        │ Source Contribution           │
├──────────────────────────┴──────────────────────────────┤
│ Feedback Trends (stacked daily bars)                     │
├──────────────────────────┬──────────────────────────────┤
│ Most Useful Articles     │ Department Engagement table   │
└──────────────────────────┴──────────────────────────────┘
```

Styling matches Xerago dashboard: slate/emerald palette, rounded-2xl cards, gradient page background.

Charts are **CSS/Tailwind** (no chart library dependency) for bundle size and consistency.

---

## Performance Considerations

1. **Parallel fetch** — `useExecutiveAnalytics` calls five endpoints with `Promise.all` (~5 simple aggregations).
2. **Read-only** — No writes; safe under scheduler load.
3. **Bounded results** — Default limits 10–20 rows per chart.
4. **No full-table scans in app code** — Aggregations delegated to MySQL.
5. **Optional caching** — Add HTTP `Cache-Control` or in-memory TTL later if dashboard traffic grows; not required for MVP.
6. **Empty states** — Charts render “No data yet” when tables are sparse (pre-production).

---

## Files

**Backend**

- `db/repositories/analytics_repository.py`
- `api/schemas/analytics.py`
- `api/routers/analytics.py`
- `api/main.py`

**Frontend**

- `pages/ExecutiveAnalytics.tsx`
- `hooks/useExecutiveAnalytics.ts`
- `types/analytics.ts`
- `components/analytics/*`
- `services/api.ts`
- `App.tsx`
- `components/dashboard/SectionHeader.tsx` (nav link)

---

## Related

- `docs/intelligence_refresh_scheduler.md` — refresh cycles in overview
- `docs/rss_source_registry.md` — source contribution metadata
