# Research Intelligence Strategy

## Purpose

This document defines how the Xerago Intelligence Engine handles **research sources** (Stanford AI, Papers With Code) in a way that supports enterprise technology radar goals—without flooding the strategic feed with academic noise.

**Principle:** Ingest broadly; promote narrowly.

---

## Strategic Intent

| Goal | Mechanism |
|------|-----------|
| Detect meaningful breakthroughs | Relevance gate + benchmark tracking |
| Support enterprise AI adoption narratives | Domain mapping to Enterprise AI, AI & ML |
| Avoid paper-of-the-day noise | Separate research store vs. strategic feed |
| Connect research to partners/clients | Entity and keyword linkage rules |

Research intelligence is **adjacent** to partner and AI vendor monitoring—not a peer priority. Most papers are stored for search and future retrieval; few become signals.

---

## Source Scope

| Source | Ingest | Promote to Strategic Feed |
|--------|--------|---------------------------|
| Stanford HAI | Yes | Selective (gate required) |
| Stanford AI Index | Yes | Annual + major updates only |
| Papers With Code — trending | Yes | Rarely |
| Papers With Code — SOTA benchmarks | Yes | When enterprise-relevant |
| arXiv (optional Phase 2) | Author/keyword watch only | Gate required |

---

## Research Artifact Types

| Type | Description | Default Destination |
|------|-------------|---------------------|
| `paper` | Academic paper with metadata | Research store |
| `benchmark_shift` | Leaderboard / SOTA change | Evaluate for promotion |
| `lab_announcement` | Institution blog post | Research store or strategic (if partner-linked) |
| `annual_report` | AI Index, survey reports | Strategic (scheduled) |
| `dataset` | New benchmark dataset | Research store only |

---

## Two-Tier Storage Model

### Tier 1 — Research Store (Broad)

- All ingested research artifacts normalized and indexed
- Searchable via API (`/v1/research/search` — Phase 2)
- Embeddings in FAISS/Qdrant for similarity (Phase 2)
- **No** summary LLM call unless artifact passes initial keyword filter (cost control)

### Tier 2 — Strategic Feed (Narrow)

- Subset that passes **Research Relevance Gate**
- Full enrichment: summary, why-it-matters, strategic score
- Appears alongside partner and OSS signals

```
100 papers ingested/week  →  ~3–8 strategic research signals/week (target)
```

---

## Research Relevance Gate

A research artifact promotes to strategic feed only if **≥1** pass condition is met:

| Rule ID | Pass Condition |
|---------|----------------|
| `RI-GATE-001` | Names ≥1 watched partner or AI vendor in title/abstract |
| `RI-GATE-002` | SOTA change on **enterprise-tracked benchmark** (see list below) |
| `RI-GATE-003` | Keyword match in **applied enterprise** lexicon (≥2 terms) |
| `RI-GATE-004` | Document type = `annual_report` from approved source |
| `RI-GATE-005` | Cited by ≥2 T1/T2 industry sources within 14 days (corroboration) |
| `RI-GATE-006` | Manual curator promotion (Phase 2 UI) |

If none pass → remain in research store only.

---

## Enterprise-Tracked Benchmarks

Benchmarks not on this list may be stored but do not trigger `RI-GATE-002`.

| Benchmark | Domain Mapping |
|-----------|----------------|
| MMLU / MMLU-Pro | AI & Machine Learning, Enterprise AI |
| HumanEval / SWE-bench | AI & Machine Learning, Automation |
| HELM (selected tasks) | Enterprise AI |
| Enterprise RAG eval suites (curated list) | AI & Machine Learning, Data Engineering |
| Marketing attribution / uplift (if on PWC) | Analytics, Martech |

Benchmark list reviewed quarterly by practice leads.

---

## Applied Enterprise Lexicon (Partial)

Papers matching **≥2** terms (stemmed) from different groups qualify for `RI-GATE-003`:

| Group | Terms |
|-------|-------|
| MarTech | marketing automation, campaign, CDP, attribution, journey orchestration |
| CX | customer experience, personalization, real-time decisioning |
| Analytics | predictive, segmentation, churn, LTV |
| Enterprise AI | RAG, agents, tool use, fine-tuning, guardrails, enterprise deployment |
| Data | feature store, pipeline, lakehouse, governance |

Pure theoretical ML with no enterprise lexicon → **no promotion**.

---

## Stanford AI — Specific Handling

| Content Type | Treatment |
|--------------|-----------|
| HAI blog — policy, industry impact | Gate via `RI-GATE-003` or entity mention |
| HAI blog — general ethics essay | Research store only |
| AI Index annual report | Auto-promote as `annual_report`; impact Strategic |
| AI Index mid-year data release | Promote if material metric shift cited in source |

---

## Papers With Code — Specific Handling

| Content Type | Treatment |
|--------------|-----------|
| Trending papers feed | Ingest all; promote <5% |
| SOTA leaderboard change | Evaluate `RI-GATE-002` |
| New dataset | Store only |
| Paper linked to HuggingFace model release | Cross-link; may merge cluster with vendor signal |

**Do not** promote solely because a paper is "trending on PWC."

---

## Enrichment Differences for Research Signals

| Field | Research-Specific Guidance |
|-------|---------------------------|
| `summary` | Plain-language: what was achieved, not jargon-heavy abstract |
| `why_it_matters` | Explicit link to Xerago client scenarios and adoption timeline (near-term vs. horizon) |
| `domains` | Minimum 1; prefer practice-aligned domains |
| `impact_level` | Cap at **High** unless `RI-GATE-002` on tier-1 benchmark → may be **Strategic** |
| `employee_relevance` | Default `specialist`; upgrade to `practice` if gate passed with partner link |

---

## Scoring Adjustments (Research)

| Factor | Adjustment |
|--------|------------|
| Base Xerago relevance | ×0.85 until gate passed, then ×1.0 |
| Innovation level | Higher for benchmark SOTA; lower for survey reports |
| Recency half-life | 240h (slower decay than incidents, faster than annual) |
| Noise penalty | +15 if no entity link and only lexicon gate |

See `scoring_model.md` for full formula.

---

## Deduplication (Research)

| Rule | Logic |
|------|-------|
| Same arXiv ID | Single cluster |
| Same paper on PWC + arXiv | Canonical = earliest published |
| Paper + vendor blog about same model | Merge into vendor-led cluster if vendor signal exists |

---

## Local-First / Cost Control

| Stage | LLM Usage |
|-------|-----------|
| Ingest | None |
| Keyword / gate pre-filter | None (rules only) |
| Summary + Why It Matters | Local Ollama or internal endpoint **only for gate-passed** |
| Embedding index | Local model preferred (Phase 2) |

Never run LLM on full firehose of papers.

---

## Metrics

| Metric | Target |
|--------|--------|
| Promotion rate | 3–8% of research artifacts |
| False positive (labeled noise) | <15% of promoted research |
| Partner-linked research in top 20 | ≥1 per week when active research cycle |
| Median time ingest → promote | < 6 hours |

---

## MVP Scope

| In Scope | Out of Scope |
|----------|--------------|
| Stanford HAI RSS ingest | arXiv broad crawl |
| PWC API or RSS for SOTA | Automatic citation graph |
| Rules-based relevance gate | ML relevance classifier |
| Research store table | Semantic search UI |
| Promoted research in API feed | Research digest email |

---

## Related Documents

- `sources.md` — Research source IDs and cadence
- `signal_rules.md` — `GATE-RI-*` and `CLS-RI-*` rules
- `categories.md` — Research Signals domain
- `scoring_model.md` — Research score modifiers
- `strategic_signal_framework.md` — Signal vs. noise philosophy
