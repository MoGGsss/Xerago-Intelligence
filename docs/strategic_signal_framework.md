# Strategic Signal Framework

## Purpose

This document is the conceptual foundation of the Xerago Intelligence Engine. It defines what a signal is, how signals differ from articles, how the platform thinks about intelligence, and how architectural layers cooperate to deliver **actionable business intelligence**—not content volume.

---

## Platform Identity

| This Platform Is | This Platform Is Not |
|------------------|----------------------|
| Enterprise Technology Radar | News aggregator |
| Strategic Intelligence Platform | RSS reader |
| Signal-quality system | AI summarization wrapper |
| Precomputed intelligence API | Real-time generation on page load |
| Standalone service (integrate later) | Replacement for existing company web app |

---

## Core Questions Every Signal Must Answer

| Question | Field / Mechanism |
|----------|-------------------|
| **What changed?** | `title`, `summary`, `signal_event_type` |
| **Why does it matter?** | `why_it_matters` |
| **Which Xerago domains are affected?** | `domains[]` |
| **How important is this update?** | `strategic_score` (0–100), `impact_level` |
| **Should employees care?** | `employee_relevance` + surfacing gates |

If an item cannot answer at least four of five convincingly, it is **not** a signal.

---

## Signal Definition

> A **signal** is a change, announcement, release, research breakthrough, ecosystem movement, or technology development that may influence Xerago services, technology strategy, partner ecosystem, or business opportunities.

### Signal vs. Artifact

| Concept | Definition | Surfaced? |
|---------|------------|-----------|
| **Artifact** | Raw ingested item (RSS entry, release JSON, paper metadata) | No |
| **Event** | Structured extraction from artifact | No |
| **Signal** | Promoted, deduplicated, scored, enriched intelligence record | Yes (if passes gates) |
| **Noise** | Artifact or event rejected by rules | Never |

### Signal Qualities (Non-Negotiable)

1. **Change-oriented** — Describes something new, not evergreen documentation.
2. **Actionable** — A practitioner can decide whether to investigate further.
3. **Provenance-clear** — Canonical source URL and trust tier attached.
4. **Deduped** — One canonical record per real-world occurrence.
5. **Pre-enriched** — Summary and Why It Matters generated asynchronously before API read.

---

## Signal Philosophy

```
Signal > Volume
```

| Principle | Implication |
|-----------|-------------|
| Aggressive filtering | Expect 80–95% of ingested artifacts to never become signals |
| Fewer, better | Top feed targets 10–20 items, not hundreds |
| Primary source wins | T1 announcements beat industry commentary |
| Lifecycle over trending | OSS tracked by release milestones, not GitHub stars |
| Research is gated | Most papers stay in research store; few promote |
| Precompute everything | No LLM calls on frontend request path |
| Fail-safe decoupling | Ingest persists even if enrichment or scoring fails |

---

## What Should Surface

| Category | Examples |
|----------|----------|
| Major AI model releases | GPT-5 class, Claude major version, Gemini enterprise tier |
| New partner capabilities | Agentforce GA, Adobe Firefly enterprise feature |
| Significant research breakthroughs | SOTA on enterprise-relevant benchmark; applied MarTech ML |
| Important OSS releases | LangGraph v1.0 → v1.1 (not re-shown without version change) |
| Major ecosystem changes | Acquisition, strategic alliance, platform deprecation |
| Enterprise AI platform announcements | watsonx, Azure OpenAI enterprise controls |
| Customer experience innovations | Autonomous journey orchestration, real-time personalization at scale |

---

## What Must NOT Surface

| Category | Suppression Mechanism |
|----------|----------------------|
| Minor bug fixes | Patch semver + no security keyword → hold |
| Small patch releases | `signal_rules.md` OSS and product rules |
| Marketing fluff | Eligibility filter + noise penalty |
| Duplicate articles | Clustering + canonical selection |
| Low-value content | Composite score below threshold |
| Repeated announcements | Cluster dedup; OSS version ledger |
| Trending repos with no release | Repository lifecycle rules |

---

## Intelligence Record Lifecycle

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   INGEST     │────▶│  NORMALIZE   │────▶│  ARTIFACT    │
│  (Layer 1)   │     │              │     │   STORE      │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                     ┌──────────────┐             │
                     │  EVENT BUS   │◀────────────┘
                     │  (Layer 2)   │
                     └──────┬───────┘
                            │
┌──────────────┐     ┌──────▼───────┐     ┌──────────────┐
│   PROCESS    │◀────│   QUEUE /    │────▶│   RETRY /    │
│  (Layer 3)   │     │   WORKERS    │     │   DEAD LETTER│
└──────┬───────┘     └──────────────┘     └──────────────┘
       │
       │  eligibility → classify → dedupe → gate
       │
┌──────▼───────┐     ┌──────────────┐     ┌──────────────┐
│  STRATEGIC   │────▶│   ENRICH     │────▶│   STORAGE    │
│  SIGNAL ENG  │     │  (LLM async) │     │  (Layer 5)   │
│  (Layer 4)   │     └──────────────┘     └──────┬───────┘
└──────────────┘                                 │
                                          ┌──────▼───────┐
                                          │  DELIVERY    │
                                          │  (Layer 6)   │
                                          │  REST API    │
                                          └──────────────┘
```

Each stage is **asynchronous** and **idempotent**. Failures at enrichment do not delete artifacts; they queue for retry.

---

## Architectural Layer Mapping

| Layer | Technology (Proposed) | Responsibility |
|-------|----------------------|----------------|
| **1 — Ingestion** | FreshRSS, GitHub API, research APIs | Collect; no business logic |
| **2 — Event Bus** | Webhooks, Redis, RabbitMQ | Decouple ingest from processing |
| **3 — Processing** | Python, FastAPI, Celery | Relevance, summarization, classification, dedup |
| **4 — Strategic Signal Engine** | Python workers | Final score, impact level, employee relevance |
| **5 — Storage** | MySQL, Redis, FAISS/Qdrant (Phase 2+) | Intelligence records, embeddings, cache |
| **6 — Delivery** | FastAPI REST (MVP); Next.js (company platform) | Slack/Teams/email later; read precomputed results only |

**Local-first:** Prefer FreshRSS, local MySQL, Redis, Ollama or internal company LLM endpoints. External AI APIs are optional fallbacks.

**Processing remains Python.** The company **Next.js + React + TypeScript** app integrates post-MVP as a read-only HTTP client.

---

## Dual Taxonomy Model

Signals carry two orthogonal classification dimensions:

| Dimension | Document | Purpose |
|-----------|----------|---------|
| **Signal Event Type** | `categories.md` (L1/L2) | *What kind of change* (release, pricing, research, …) |
| **Xerago Domain** | `categories.md` (domains) | *Which practices are affected* (Martech, CX, …) |

Scoring uses both: event type affects base weight; domain mapping affects Xerago relevance factor.

---

## Strategic Score and Impact Level

| Field | Scale | Purpose |
|-------|-------|---------|
| `strategic_score` | 0–100 | Quantitative ranking |
| `impact_level` | Low \| Medium \| High \| Strategic | Human-readable urgency band |

Derived from multi-factor model in `scoring_model.md`. Impact level is **not** independent opinion—it is computed from score bands plus override rules for incidents and deprecations.

---

## Employee Relevance

`employee_relevance` indicates whether a typical Xerago employee should be notified or briefed.

| Value | Meaning |
|-------|---------|
| `broadcast` | Score ≥ 85 or Strategic impact; practice-wide interest |
| `practice` | Score 65–84; relevant to specific domains |
| `specialist` | Score 45–64; architects, leads, niche roles |
| `archive` | Stored but not pushed; score < 45 or research-only |

MVP may omit push notifications; field is still stored for future Slack/digest routing.

---

## Feedback Loop (Future)

User actions improve relevance over time:

| Action | Effect |
|--------|--------|
| **Useful** | Boost similar domain/entity patterns (+decay over 90d) |
| **Not Useful** | Increase noise penalty for similar patterns |
| **More Like This** | Temporary boost to cluster embedding neighbors |
| **Ignore Similar** | Suppression rule for simhash/embedding neighborhood |

Feedback never deletes source data; it adjusts scoring weights per user cohort (Phase 2+).

---

## Source Priority Hierarchy

| Priority | Group | Rationale |
|----------|-------|-----------|
| **P0** | Partner ecosystem | Highest business alignment with Xerago services |
| **P1** | AI vendors | Drives enterprise AI strategy for clients |
| **P2** | Open source (curated repos) | Implementation and integration risk |
| **P3** | Research | Innovation radar; heavily gated |
| **P4** | Industry intelligence | Narrative and corroboration only |

---

## Governance

| Artifact | Owner | Cadence |
|----------|-------|---------|
| Signal definition & framework | Principal Architect | Per major release |
| Source registry | Platform + practice leads | Monthly |
| Scoring weights | Platform + calibration labels | Bi-weekly during pilot |
| Repository watchlist | Technical architecture practice | Quarterly |
| Domain taxonomy | Chief Architect + practice leads | Semi-annual |

---

## Related Documents

| Document | Scope |
|----------|-------|
| `sources.md` | Source taxonomy and registry |
| `categories.md` | Domain + event type taxonomy |
| `signal_rules.md` | Promotion and suppression rules |
| `scoring_model.md` | Strategic score computation |
| `output_schema.md` | API payload contract |
| `repository_tracking_strategy.md` | OSS lifecycle rules |
| `research_intelligence_strategy.md` | Research gating and promotion |
| `product_requirements.md` | Functional and non-functional requirements |
| `roadmap.md` | MVP and phased delivery |
