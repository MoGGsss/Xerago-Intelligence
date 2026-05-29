# Strategic Scoring Model

## Purpose

This document defines how intelligence records receive a **Strategic Score (0–100)** and an **Impact Level** (Low | Medium | High | Strategic). Scoring runs in **Layer 4 — Strategic Signal Engine** after processing and before storage. All scores are **precomputed**; APIs return stored values only.

---

## Design Goals

1. **Signal over volume** — High threshold for strategic feed inclusion
2. **Xerago-centric** — Partner and practice relevance outweigh generic hype
3. **Explainable** — Factor breakdown stored on every record
4. **Calibratable** — Weights tuned via human feedback loop (future)
5. **Aligned to employee decisions** — `employee_relevance` derived from score + rules

---

## Output Fields

| Field | Type | Description |
|-------|------|-------------|
| `strategic_score` | integer 0–100 | Primary ranking metric |
| `impact_level` | enum | Low \| Medium \| High \| Strategic |
| `employee_relevance` | enum | broadcast \| practice \| specialist \| archive |
| `score_breakdown` | object | Factor contributions for explainability |

---

## Composite Formula

Internal factors are computed on a **0.0–1.0** scale, combined, then mapped to 0–100.

```
raw = (W_x × xerago_relevance)
    + (W_p × partner_relevance)
    + (W_e × enterprise_applicability)
    + (W_i × innovation_level)
    + (W_s × source_trust)
    + (W_r × recency)
    - (W_n × noise_penalty)

strategic_score = round(clamp(raw, 0, 1) × 100)
```

### Default Weights

| Factor | Symbol | Weight | Description |
|--------|--------|--------|-------------|
| Xerago relevance | `W_x` | 0.22 | Domain + practice alignment |
| Partner relevance | `W_p` | 0.20 | Partner ecosystem priority |
| Enterprise applicability | `W_e` | 0.18 | Client deployability near-term |
| Innovation level | `W_i` | 0.15 | Novelty and capability leap |
| Source trust | `W_s` | 0.12 | T1/T2/T3 tier |
| Recency | `W_r` | 0.10 | Time decay |
| Noise penalty | `W_n` | subtract ≤0.25 | Fluff, rumor, duplicate patterns |

Config version: `scoring_v2.0.0`

---

## Factor Definitions

### 1. Xerago Relevance (`xerago_relevance`)

How directly the signal maps to Xerago domains and services.

| Input | Score contribution |
|-------|-------------------|
| Primary domain ∈ {martech, customer-experience, personalization, analytics} | +0.25 base |
| Primary domain ∈ {enterprise-ai, ai-ml, automation} | +0.20 base |
| Primary domain = research-signals only | +0.10 base |
| Primary domain = industry-trends only | +0.05 base |
| ≥2 practice-aligned domains | +0.10 |
| Explicit product line match (Marketo, Agentforce, etc.) | +0.10 |
| LLM why-it-matters cites client migration/delivery risk | +0.05 (capped) |

```
xerago_relevance = min(1.0, sum(components))
```

---

### 2. Partner Relevance (`partner_relevance`)

| Entity Group | Base |
|--------------|------|
| Partner (Adobe, Salesforce, …) | 1.00 |
| AI vendor | 0.85 |
| OSS (Tier A registry) | 0.75 |
| Research (gate passed) | 0.65 |
| Industry (T2 only) | 0.40 |

Modifier: +0.10 if signal affects ≥2 partners (ecosystem shift).

---

### 3. Enterprise Applicability (`enterprise_applicability`)

| Indicator | Points |
|-----------|--------|
| GA / production-ready language | +0.25 |
| Enterprise SKU, admin controls, SSO, audit | +0.20 |
| Quantified business outcome (%, $, time) | +0.15 |
| Migration or breaking change for enterprises | +0.20 |
| Experimental / lab-only with no product path | cap at 0.35 |

Default if no indicators: **0.30**

---

### 4. Innovation Level (`innovation_level`)

| Indicator | Points |
|-----------|--------|
| New category of capability (first-of-kind for entity) | +0.35 |
| Major semver / major model generation | +0.30 |
| Benchmark SOTA (enterprise list) | +0.30 |
| Incremental feature in existing line | +0.15 |
| Repackaged or restated prior announcement | +0.05 |

---

### 5. Source Trust (`source_trust`)

| Tier | Value |
|------|-------|
| T1 | 1.00 |
| T2 | 0.60 |
| T3 | 0.30 (cannot surface alone) |

| Modifier | Delta |
|----------|-------|
| GitHub release (verified registry) | +0.05 |
| Corroborated T1 + T2 | +0.10 |

---

### 6. Recency (`recency`)

Exponential decay by event L1 half-life (hours):

| Event L1 | Half-life |
|----------|-----------|
| operational-incident | 12 |
| product-technology | 72 |
| go-to-market | 96 |
| partnership-ecosystem | 120 |
| market-narrative | 48 |
| research-innovation | 240 |

```
recency = exp(-λ × age_hours)
```

---

### 7. Noise Penalty (`noise_penalty`)

| Condition | Penalty |
|-----------|---------|
| L1 = market-narrative | +0.12 |
| L2 = rumor-unconfirmed | +0.18 |
| Marketing fluff heuristic | +0.10 |
| Industry-only, no T1 corroboration | +0.15 |
| Low classification confidence | +0.05 |
| User feedback "not useful" pattern (future) | +0.10 |

---

## Impact Level Mapping

Impact level is **derived** from strategic score and override rules.

| Strategic Score | Default Impact Level |
|-----------------|----------------------|
| 85–100 | **Strategic** |
| 70–84 | **High** |
| 50–69 | **Medium** |
| 0–49 | **Low** |

### Override Rules (take highest applicable)

| Condition | Minimum Impact |
|-----------|----------------|
| L2 = `deprecation-eol` on P0 partner | High |
| L2 = `acquisition` involving watched entity | Strategic |
| Security CVE on Tier A OSS | High |
| Active P0 partner outage | High |
| AI Index annual report | Strategic |
| Research benchmark SOTA (tier-1 list) | High |

---

## Employee Relevance Mapping

| Condition | employee_relevance |
|-----------|-------------------|
| impact_level = Strategic OR strategic_score ≥ 85 | `broadcast` |
| impact_level = High OR score 65–84 | `practice` |
| score 45–64 | `specialist` |
| score < 45 OR research-only store | `archive` |

---

## Surfacing Thresholds

| Feed | Min Strategic Score | Max Items | Notes |
|------|---------------------|-----------|-------|
| **Strategic Top** | 55 | 20 | Diversity by entity |
| **Partner watch** | 40 | 50 | Per-entity API |
| **Research promoted** | 50 | 10/week target | Gate required |
| **OSS releases** | 45 | Tier-based | Ledger dedup |

**Philosophy:** Most employees see only items ≥ 55 in default digest.

---

## Example Calculation

**Salesforce autonomous journey orchestration** (illustrative):

| Factor | Value | Weighted |
|--------|-------|----------|
| Xerago relevance | 0.90 | 0.20 |
| Partner relevance | 1.00 | 0.20 |
| Enterprise applicability | 0.85 | 0.15 |
| Innovation level | 0.70 | 0.11 |
| Source trust | 1.00 | 0.12 |
| Recency | 0.95 | 0.10 |
| Noise penalty | 0.02 | −0.02 |
| **Raw** | | **0.86** |

→ `strategic_score = 86`  
→ `impact_level = Strategic`  
→ `employee_relevance = broadcast`

---

## Ranking and Diversity

Sort: `strategic_score DESC`, `published_at DESC`.

| Rule | Limit |
|------|-------|
| Max per entity in top 20 | 4 |
| Max market-narrative in top 20 | 3 |
| Max OSS in top 20 | 5 |

---

## Feedback Loop Adjustments (Future)

| User Action | Scoring Effect |
|-------------|----------------|
| Useful | +3 to similar domain/entity (30d decay) |
| Not useful | +5 noise penalty pattern (60d) |
| More like this | +8 temporary boost for embedding neighbors |
| Ignore similar | Suppress simhash neighborhood |

Stored in `user_feedback` table; never mutates source artifacts.

---

## Calibration

| Metric | MVP Target | Mature Target |
|--------|------------|---------------|
| precision@10 | ≥ 0.75 | ≥ 0.85 |
| % ingested → strategic | 5–12% | 5–10% |
| Median score in top 10 | 72–88 | 75–90 |

Weekly labeling by practice leads during pilot.

---

## Related Documents

- `strategic_signal_framework.md` — Philosophy and layers
- `signal_rules.md` — Gates before scoring
- `output_schema.md` — Field contract
- `categories.md` — Domain mapping for Xerago relevance
- `research_intelligence_strategy.md` — Research score caps
