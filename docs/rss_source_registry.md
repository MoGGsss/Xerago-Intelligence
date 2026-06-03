# RSS Source Registry (Phase 8)

## Purpose

Phase 8 expands RSS coverage for the Xerago Intelligence Engine with a **centralized, database-backed registry** that drives scheduled ingestion, health monitoring, and operational statistics—without changing the enrichment pipeline.

The YAML registry (`registry/sources.yaml`) remains the long-term taxonomy and documentation source; **`rss_sources`** is the operational feed list used by the ingest scheduler.

---

## Architecture

```mermaid
flowchart LR
  subgraph catalog [Seed Catalog]
    SC[source_catalog.py]
  end
  subgraph db [MySQL]
    RS[rss_sources]
    RR[rss_source_runs]
    AR[artifacts]
    IC[ingest_cursors]
  end
  subgraph ingest [Ingestion]
    SCH[IngestionScheduler]
    HM[SourceHealthMonitor]
    RSS[RssIngestionService]
  end
  subgraph enrich [Unchanged]
    ENR[ArtifactEnrichmentService]
  end
  subgraph api [API]
    ST[/v1/sources/stats]
    HL[/v1/sources/health]
  end

  SC -->|seed_rss_sources.py| RS
  SCH --> RS
  SCH --> HM --> RSS --> AR
  RSS --> IC
  SCH --> ENR
  RS --> ST
  RR --> HL
```

### Components

| Component | Role |
|-----------|------|
| `ingest/source_catalog.py` | Canonical Phase 8 feed definitions (19 sources, tiers 1–3) |
| `rss_sources` | Active registry: name, site URL, RSS URL, tier, health summary |
| `rss_source_runs` | Per-cycle ingest metrics and errors |
| `SourceHealthMonitor` | Wraps fetch/parse/persist; records success/failure |
| `IngestionScheduler` | Loads active rows from DB; auto-seeds if empty |
| `artifacts.uq_artifacts_url` | **Global duplicate protection** across all feeds |

---

## Database Schema

### `rss_sources`

| Column | Description |
|--------|-------------|
| `source_id` | Stable kebab-case ID (aligned with `registry/sources.yaml` where applicable) |
| `source_name` | Display name |
| `source_url` | Canonical site URL |
| `rss_url` | Feed URL (unique) |
| `source_tier` | `1` (AI/strategic), `2` (research/industry), `3` (partners) |
| `active_flag` | Enable/disable polling |
| `failure_count` | Consecutive failures (resets on success) |
| `last_health_status` | `healthy`, `degraded` (1–2 failures), `unhealthy` (3+) |
| `last_success_at` / `last_failure_at` / `last_run_at` | Timestamps |

### `rss_source_runs`

One row per scheduler cycle per source: fetched/inserted/skipped counts, HTTP status, error message.

**Apply schema:** `python backend/scripts/apply_schema.py`  
**Seed feeds:** `python backend/scripts/seed_rss_sources.py`

---

## Source Tiers and Feeds

### Tier 1 — AI vendors (8)

| Source | RSS URL |
|--------|---------|
| OpenAI | `https://openai.com/news/rss.xml` |
| Google AI Blog | `https://blog.google/technology/ai/rss/` |
| Microsoft AI Blog | `https://blogs.microsoft.com/ai/feed/` |
| Anthropic | `https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml` |
| Adobe | `https://medium.com/feed/adobetech` |
| Salesforce AI | `https://www.salesforce.com/blog/feed/` |
| IBM AI | `https://research.ibm.com/rss` |
| HuggingFace | `https://huggingface.co/blog/feed.xml` |

### Tier 2 — Research & industry (6)

| Source | RSS URL |
|--------|---------|
| Stanford HAI | `https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_the_batch.xml` |
| Papers With Code | `https://rss.arxiv.org/rss/cs.LG` |
| TLDR AI | `https://bullrich.dev/tldr-rss/ai.rss` |
| TechCrunch AI | `https://techcrunch.com/category/artificial-intelligence/feed/` |
| The Verge AI | `https://www.theverge.com/rss/ai-artificial-intelligence/index.xml` |
| MIT Technology Review AI | `https://www.technologyreview.com/topic/artificial-intelligence/feed/` |

### Tier 3 — Partners (5)

| Source | RSS URL |
|--------|---------|
| Acquia | `https://www.acquia.com/blog/rss.xml` |
| SAS | `https://blogs.sas.com/content/feed/?x=1` |
| HCL | `https://www.hcl-software.com/blog/feed` |
| Unica | `https://www.salesforce.com/blog/category/marketing/feed/` |
| Acoustic | `https://www.tealium.com/blog/feed/` |

---

## Health Monitoring

After each poll:

1. **Success** — `failure_count` reset; `last_health_status = healthy`; run row `status = success`.
2. **Fetch/parse failure** — increment `failure_count`; `degraded` or `unhealthy`; run row `status = failure`.
3. Per-source failures do not block other sources in the same scheduler cycle.

Inspect health:

- `GET /v1/sources` — registry snapshot  
- `GET /v1/sources/health` — registry + recent runs  
- `GET /v1/sources/stats` — artifact counts and daily volume estimates  

---

## Duplicate Protection

Duplicates are prevented **across all feeds**, not per `source_id`:

1. URLs normalized via `normalize_url()` (fragment stripped, host lowercased).
2. `ArtifactRepository.insert_article()` checks existing URL before insert.
3. MySQL unique index `uq_artifacts_url` on `artifacts.url`.

The same article syndicated on TechCrunch and a vendor blog is stored once; the second ingest increments `skipped_duplicate`.

---

## Enrichment

No changes to `ArtifactEnrichmentService`, negative filter, department mapping, or scoring. New artifacts from expanded RSS feeds follow the existing post-insert enrichment loop in `IngestionScheduler`.

---

## Estimated Daily Article Volume

Planning estimates (before live ingest history):

| Tier | Sources | Est. articles/day each | Subtotal |
|------|---------|------------------------|----------|
| 1 | 8 | ~2.5 | ~20 |
| 2 | 6 | ~8.0 | ~48 |
| 3 | 5 | ~1.2 | ~6 |
| **Total** | **19** | | **~74 raw articles/day** |

Notes:

- Industry feeds (Tier 2) dominate volume; many items are filtered by the negative intelligence filter before enrichment.
- After 24h of ingest, `GET /v1/sources/stats` uses actual `artifacts_last_24h` per source instead of tier defaults.
- Scheduler interval (default 15 minutes) × 19 sources ≈ **1,824 feed polls/day**; most cycles return zero new rows due to cursors and duplicates.

---

## Operations

```bash
# Schema + seed
cd backend
python scripts/apply_schema.py
python scripts/seed_rss_sources.py

# Disable a feed without deleting history
# UPDATE rss_sources SET active_flag = 0 WHERE source_id = 'tc-ai';
```

---

## Related Documents

- `docs/sources.md` — Full source taxonomy (YAML registry)
- `docs/negative_intelligence_filter.md` — Post-ingest filtering
- `registry/sources.yaml` — Entity and source metadata
