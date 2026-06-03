# Negative Intelligence Filter

## Purpose

Pre-enrichment gate that skips LLM enrichment for off-topic or noisy articles using a centralized global keyword list.

Version: `neg_filter_v1.0.0`  
Rule ID: `NEG-FILTER-001`

---

## Pipeline placement

```
Ingest → artifacts → NegativeFilter → (skip | enrich → score → department map)
```

Runs inside `ArtifactEnrichmentService.enrich_artifact()` **before** the LLM call. Strategic scoring and department mapping are unchanged.

---

## Global negative keywords

celebrity, actor, actress, movie, cinema, football, cricket, soccer, lottery, betting, gambling, coupon, discount, sale, giveaway, memecoin, politics, rumor, gossip

**Phrases:** crypto price, bitcoin prediction

**Sale allowlist:** salesforce, sales cloud, sales program, sales team, upsell, cross-sell

---

## Scoring

| Match | Points |
|-------|--------|
| Phrase in title | 5 |
| Phrase in body | 3 |
| Keyword in title | 3 |
| Keyword in body | 1 |

Skip when `negative_score >= threshold` (default **5**).

---

## Persistence

Table: `artifact_filter_decisions`

| Column | Description |
|--------|-------------|
| `decision` | `passed` \| `skipped` |
| `skip_reason` | Rule ID + score + matched terms |
| `matched_keywords` | JSON array |
| `filter_version` | Rule set version |

Skipped artifacts remain in `artifacts` for audit but never receive enrichment rows.

---

## Configuration

| Env var | Default |
|---------|---------|
| `NEGATIVE_FILTER_ENABLED` | `true` |
| `NEGATIVE_SCORE_SKIP_THRESHOLD` | `5` |

---

## Scripts

```bash
python scripts/backfill_negative_filter.py
python scripts/backfill_negative_filter.py --force
python tests/test_negative_filter.py
```

---

## Related

- `docs/signal_rules.md` — eligibility / suppression philosophy
- `backend/src/xerago_intelligence/filtering/` — implementation
