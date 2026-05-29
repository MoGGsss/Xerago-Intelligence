# Signal Rules

## Purpose

This document defines how raw ingested artifacts become **intelligence records (signals)**, how noise is reduced, and how duplicates are collapsed.

**Philosophy:** Signal > Volume. Aggressive filtering is a core feature—not a bug.

Rules execute in **Layer 3 (Processing)** before **Layer 4 (Strategic Signal Engine)**. All processing is **async** via queue workers; failures retry without losing artifacts.

---

## Definitions

| Term | Definition |
|------|------------|
| **Artifact** | Raw normalized document from a source (HTML, RSS item, release JSON) |
| **Event** | Structured extraction from an artifact (title, body, URLs, timestamps, entities) |
| **Signal** | A promoted event that passed eligibility, dedup, and gating rules |
| **Cluster** | Group of events describing the same real-world occurrence |
| **Canonical signal** | The single representative signal chosen from a cluster |

---

## Pipeline Stages

```
Ingest → Normalize → Extract Event → Eligibility Filter → Classify
    → Dedupe Cluster → Gate → Enrich → Score → Surface
```

Each stage emits structured audit metadata for explainability.

---

## Stage 1: Eligibility Filter

Artifacts that **fail** eligibility are stored for audit but never become signals.

### Hard Exclusions (Drop)

| Rule ID | Condition | Action |
|---------|-----------|--------|
| `ELIG-001` | Empty or non-English body (< 50 chars meaningful text) without translation path | Drop |
| `ELIG-002` | Source `enabled = false` | Drop |
| `ELIG-003` | Published date older than **180 days** on first ingest (unless `annual-report` subcategory) | Drop |
| `ELIG-004` | URL matches blocklist (spam, unrelated domains) | Drop |
| `ELIG-005` | Content classified as pure marketing fluff with no factual claim (see heuristic below) | Drop |

**Marketing fluff heuristic:** No product name, version, date, metric, or proper noun entity → drop.

### Soft Exclusions (Hold for Review)

| Rule ID | Condition | Action |
|---------|-----------|--------|
| `ELIG-101` | Entity confidence < 0.60 | Hold |
| `ELIG-102` | Category confidence < 0.75 | Hold |
| `ELIG-103` | T3-only source with no T1/T2 link | Hold |

Hold queue reviewed weekly or on client escalation path (Phase 2).

---

## Stage 2: Event Extraction Requirements

Minimum viable event fields:

| Field | Required | Notes |
|-------|----------|-------|
| `event_id` | Yes | UUID v7 |
| `source_id` | Yes | From registry |
| `canonical_url` | Yes | Deduped, tracking params stripped |
| `title` | Yes | Normalized whitespace |
| `published_at` | Yes | Source timestamp preferred over fetch time |
| `body_text` | Yes | Main content, boilerplate removed |
| `entity_tags` | ≥1 | From watchlist |
| `content_hash` | Yes | Simhash of normalized body |

---

## Stage 3: Classification Rules (Rules-First)

Rules execute before ML classifier. First match wins for L2 unless overridden by ML confidence > 0.90.

### Product & Technology

| Rule ID | Trigger | L1 | L2 |
|---------|---------|----|----|
| `CLS-PT-001` | GitHub release semver major bump (`MAJOR >= 1` change) | product-technology | major-release |
| `CLS-PT-002` | Keywords: `deprecated`, `end of life`, `EOL`, `breaking change` | product-technology | deprecation-eol |
| `CLS-PT-003` | Keywords: `generally available`, `GA`, `now available` + product name | product-technology | feature-addition |
| `CLS-PT-004` | GitHub release with `security` label or CVE reference | product-technology | security-patch |
| `CLS-PT-005` | Changelog entry with API endpoint path pattern | product-technology | api-platform |

### Go-to-Market

| Rule ID | Trigger | L1 | L2 |
|---------|---------|----|----|
| `CLS-GTM-001` | Keywords: `pricing`, `price`, `% off`, `per token`, `per seat` + numeric change | go-to-market | pricing-change |
| `CLS-GTM-002` | Keywords: `new edition`, `SKU`, `bundle`, `tier` | go-to-market | packaging-sku |
| `CLS-GTM-003` | Keywords: `now available in`, `region`, `data residency` | go-to-market | availability-geo |

### Partnership & Ecosystem

| Rule ID | Trigger | L1 | L2 |
|---------|---------|----|----|
| `CLS-PE-001` | Keywords: `acquires`, `acquisition of`, `to acquire` | partnership-ecosystem | acquisition |
| `CLS-PE-002` | Keywords: `partners with`, `strategic partnership`, `collaboration` + named entity | partnership-ecosystem | strategic-alliance |
| `CLS-PE-003` | Keywords: `integration with`, `connector`, `available on AppExchange` | partnership-ecosystem | integration-connector |

### Research

| Rule ID | Trigger | L1 | L2 |
|---------|---------|----|----|
| `CLS-RI-001` | Source ∈ {Stanford HAI, Papers With Code} + paper metadata | research-innovation | foundation-model |
| `CLS-RI-002` | Benchmark name in tracked list + "new SOTA" or leaderboard rank 1 | research-innovation | benchmark-sota |
| `CLS-RI-003` | Title contains `AI Index` or `annual report` | research-innovation | annual-report |

### Operational Incident

| Rule ID | Trigger | L1 | L2 |
|---------|---------|----|----|
| `CLS-OI-001` | Source is status page OR keywords: `outage`, `degraded`, `incident` | operational-incident | outage-degradation |
| `CLS-OI-002` | Keywords: `postmortem`, `resolved`, `restored` | operational-incident | incident-resolved |

### Market Narrative (Default Fallback for T2)

| Rule ID | Trigger | L1 | L2 |
|---------|---------|----|----|
| `CLS-MN-001` | Source tier = T2 AND no T1 rule matched | market-narrative | thought-leadership |
| `CLS-MN-002` | Keywords: `rumor`, `reportedly`, `leak` without T1 source | market-narrative | rumor-unconfirmed |

---

## Stage 4: Research Relevance Gate

Research signals require additional promotion criteria to enter the **strategic feed**.

| Rule ID | Gate Condition | Result |
|---------|----------------|--------|
| `GATE-RI-001` | L2 = `benchmark-sota` AND benchmark ∈ tracked enterprise list (MMLU, HumanEval, SWE-bench, …) | Pass |
| `GATE-RI-002` | Paper cites or names ≥1 watched partner/AI entity | Pass |
| `GATE-RI-003` | L2 = `applied-enterprise` AND keywords match MarTech/CDP/analytics lexicon | Pass |
| `GATE-RI-004` | L2 = `annual-report` | Pass |
| `GATE-RI-005` | None of above | **Research-only feed** (not strategic top-N) |

---

## Stage 5: Deduplication and Clustering

Goal: **one canonical signal per real-world event**, avoiding duplicate cards in the UI.

### URL-Level Dedup

| Rule ID | Logic |
|---------|-------|
| `DEDUP-001` | Normalize URL: strip UTM params, lowercase host, remove trailing slash |
| `DEDUP-002` | Exact `canonical_url` match → same cluster |
| `DEDUP-003` | `content_hash` exact match → same cluster (even if URL differs) |

### Semantic Clustering

| Rule ID | Logic |
|---------|-------|
| `DEDUP-101` | Simhash Hamming distance ≤ 3 → candidate cluster |
| `DEDUP-102` | Title fuzzy ratio ≥ 0.88 AND same primary entity AND published within 72h → same cluster |
| `DEDUP-103` | GitHub release: same repo + same tag → same cluster |

### Canonical Selection (Winner Within Cluster)

Priority order:

1. **Highest trust tier** (T1 > T2 > T3)
2. **Earliest published_at** (original announcement wins)
3. **Richer body** (longer substantive content)
4. **Preferred source type:** press/blog > industry > aggregator

Non-canonical events are linked as `related_sources[]` on the canonical signal.

---

## Stage 6: Noise Reduction

### Velocity Caps

| Rule ID | Scope | Limit |
|---------|-------|-------|
| `NOISE-001` | Same entity + L2 `thought-leadership` | Max 2 per 24h in strategic feed |
| `NOISE-002` | Same entity + any category | Max 10 signals per 24h surfaced |
| `NOISE-003` | HuggingFace trending models | Max 1 per 12h unless partner-linked |

### Promotional Content Suppression

| Rule ID | Condition | Action |
|---------|-----------|--------|
| `NOISE-101` | Title matches webinar/event invite pattern without product news | Suppress |
| `NOISE-102` | > 60% of body is boilerplate CTA / registration links | Suppress |
| `NOISE-103` | Duplicate press recycle: cluster already has T1 canonical < 7 days old | Suppress new T2 variant |

### Incident Decay

| Rule ID | Condition | Action |
|---------|-----------|--------|
| `NOISE-201` | L1 = operational-incident AND L2 = incident-resolved | Remove from top feed after 24h |
| `NOISE-202` | Unresolved incident > 14 days | Flag stale; reduce score 50% |

---

## Stage 7: OSS Lifecycle Rules

See `repository_tracking_strategy.md`. Summary:

| Rule ID | Requirement |
|---------|-------------|
| `OSS-001` | Version exists in ledger → suppress |
| `OSS-002` | Patch bump Tier B/C without security → suppress |
| `OSS-003` | Draft/prerelease → hold (Tier A security excepted) |

---

## Stage 8: Surfacing Gates (Strategic Feed)

A record is set to `status: published` and appears in the strategic feed only if:

| Rule ID | Requirement |
|---------|-------------|
| `SURF-001` | Passed eligibility (not dropped, not in hold) |
| `SURF-002` | Is canonical in its cluster |
| `SURF-003` | `strategic_score` ≥ 55 (see `scoring_model.md`) |
| `SURF-004` | L1 ≠ market-narrative OR corroborated by T1 within 7 days |
| `SURF-005` | L2 ≠ rumor-unconfirmed OR T1 corroboration exists |
| `SURF-006` | Research signals passed `GATE-RI-*` or `RI-GATE-*` |
| `SURF-007` | Required enrichment complete (summary, why_it_matters, domains) |

### Feed Tiers

| Feed | Inclusion Criteria |
|------|-------------------|
| **Strategic Top** | SURF-* passed; ranked by composite score |
| **Entity Watch** | All canonical signals for selected entity (score ≥ 0.35) |
| **Research** | research-innovation L1, relevance gate optional |
| **Incidents** | operational-incident L1, active only |

---

## GitHub Release Rules

| Signal | Condition |
|--------|-----------|
| Always promote | Major semver bump |
| Always promote | Release notes contain `breaking`, `security`, `CVE` |
| Promote | Minor semver + keywords: `performance`, `new feature`, `API` |
| Hold | Patch semver unless security-related |
| Link | Attach repo, tag, release URL, diff summary |

Release signals inherit entity from repo registry mapping.

---

## Summarization and "Why It Matters" Triggers

Enrichment runs on promoted signals only.

| Rule ID | Trigger | Enrichment |
|---------|---------|------------|
| `ENR-001` | Promoted to signal (passed gates) | Generate summary (≤ 120 words) |
| `ENR-002` | `strategic_score` ≥ 50 OR L1 ∈ {product-technology, go-to-market, regulatory-trust} | Generate "Why It Matters" |
| `ENR-003` | L2 = major-release OR acquisition | Generate consultant action hint (Phase 2) |

Summaries must cite canonical source URL. "Why It Matters" is framed for Xerago client impact (MarTech, CDP, AI governance, migration risk).

---

## Audit and Explainability

Every signal stores:

```
promotion_trace[]   — Rule IDs fired at each stage
cluster_id          — Dedup cluster reference
canonical           — boolean
suppressed_reason   — null or rule ID
gate_status         — passed | failed | research-only
confidence          — classification confidence
```

Enables UI "Why am I seeing this?" drill-down.

---

## Rule Governance

| Activity | Owner | Frequency |
|----------|-------|-----------|
| Rule tuning | Platform + practice lead | Bi-weekly during pilot |
| False positive review | Curator | Weekly |
| Blocklist updates | Platform | As needed |
| Regression tests on rule changes | Engineering | Every release |

---

## Related Documents

- `sources.md` — Source trust tiers feed dedup priority
- `categories.md` — L1/L2 taxonomy referenced by classification rules
- `scoring_model.md` — Composite score threshold for surfacing
- `output_schema.md` — Signal payload including cluster and trace fields
