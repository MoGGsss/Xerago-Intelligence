# Product Requirements Document (PRD)

## Xerago Intelligence Engine

| Field | Value |
|-------|-------|
| **Product** | Xerago Intelligence Engine |
| **Type** | Enterprise Technology Radar & Strategic Intelligence Platform |
| **Version** | 1.0 (MVP) |
| **Status** | Architecture / Pre-implementation |
| **Owner** | Xerago — Enterprise Architecture |

---

## 1. Executive Summary

The Xerago Intelligence Engine continuously monitors partner ecosystems, AI vendors, research communities, open-source repositories, and industry sources. It converts high-volume raw information into **few, high-quality, precomputed intelligence records** that answer what changed, why it matters, which Xerago domains are affected, and how important the update is.

The product is **not** a news aggregator, RSS reader, or on-demand summarization tool. It is a **standalone service** built and validated before integration into the existing company web platform.

---

## 2. Problem Statement

Xerago practitioners lack a unified, low-noise view of strategic technology change across partners and AI ecosystems. Manual monitoring is fragmented, duplicate-heavy, and inconsistent. Teams need **actionable intelligence**, not more articles.

---

## 3. Product Vision

> Maximize signal quality while minimizing noise.

Deliver an automated pipeline:

```
Collect → Filter → Summarize → Explain Impact → Detect Signals → Dedupe → Score → Store → API
```

---

## 4. Goals and Non-Goals

### Goals (MVP)

| ID | Goal |
|----|------|
| G1 | Reliable pipeline: article → summary → why-it-matters → strategic score → stored record |
| G2 | Aggressive noise reduction and duplicate elimination |
| G3 | Partner ecosystem monitoring (P0 sources) |
| G4 | OSS lifecycle monitoring (no re-surface without version change) |
| G5 | Precomputed intelligence; REST API read path only |
| G6 | Local-first deployment (FreshRSS, MySQL, Redis, local/internal LLM) |

### Non-Goals (MVP)

| ID | Non-Goal |
|----|----------|
| NG1 | Frontend UI or dashboard |
| NG2 | Integration into existing company website |
| NG3 | Slack, Teams, or email digest delivery |
| NG4 | Enterprise multi-tenant scaling |
| NG5 | User feedback loop implementation (documented for Phase 2) |
| NG6 | Broad web crawl or social media monitoring |

---

## 5. Users and Stakeholders

| Persona | Need |
|---------|------|
| **Consultant / Practitioner** | Know what partner/AI changes affect client delivery |
| **Practice Lead** | Curate signal quality; calibrate scoring |
| **Solution Architect** | Track OSS, APIs, deprecations, integrations |
| **Executive (future)** | Scan top strategic moves weekly |
| **Platform Engineer** | Operate ingestion and workers reliably |

MVP primary user: **internal practitioners via API** (CLI, Postman, or thin internal tools—not production website).

---

## 6. Functional Requirements

### 6.1 Ingestion (Layer 1)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-ING-01 | Ingest RSS/Atom from partner blogs and press rooms via FreshRSS | P0 |
| FR-ING-02 | Ingest AI vendor blogs and changelogs | P0 |
| FR-ING-03 | Poll GitHub Releases for registry repos (lifecycle rules) | P0 |
| FR-ING-04 | Ingest industry sources (TechCrunch AI, Verge AI, TLDR AI) | P1 |
| FR-ING-05 | Ingest Stanford HAI and Papers With Code | P1 |
| FR-ING-06 | Persist raw artifacts with provenance (`source_id`, URL, timestamp) | P0 |
| FR-ING-07 | Emit events to bus on new artifact (webhook or queue message) | P0 |

### 6.2 Processing (Layer 3)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-PROC-01 | Normalize artifacts to common event envelope | P0 |
| FR-PROC-02 | Apply eligibility filters (drop fluff, stale, blocked) | P0 |
| FR-PROC-03 | Classify signal event type (L1/L2) | P0 |
| FR-PROC-04 | Map Xerago domains (1–4 per record) | P0 |
| FR-PROC-05 | Cluster and deduplicate; select canonical signal | P0 |
| FR-PROC-06 | Apply research relevance gate before promotion | P1 |
| FR-PROC-07 | Enforce OSS version ledger (no repeat without new version) | P0 |

### 6.3 Enrichment

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-ENR-01 | Generate concise summary (async, precomputed) | P0 |
| FR-ENR-02 | Generate "Why It Matters" for Xerago business context | P0 |
| FR-ENR-03 | Use local Ollama or internal company LLM endpoint by default | P0 |
| FR-ENR-04 | Retry enrichment on failure without losing artifact | P0 |

### 6.4 Strategic Signal Engine (Layer 4)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-SIG-01 | Compute `strategic_score` (0–100) | P0 |
| FR-SIG-02 | Assign `impact_level` (Low, Medium, High, Strategic) | P0 |
| FR-SIG-03 | Assign `employee_relevance` | P1 |
| FR-SIG-04 | Store explainable `score_breakdown` | P0 |
| FR-SIG-05 | Suppress signals below strategic feed threshold (default score < 55) | P0 |

### 6.5 Storage (Layer 5)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-STOR-01 | MySQL as system of record for intelligence records | P0 |
| FR-STOR-02 | Redis for queue/cache | P0 |
| FR-STOR-03 | Version ledger for OSS repos | P0 |
| FR-STOR-04 | Research store for non-promoted papers | P1 |
| FR-STOR-05 | Vector index (FAISS/Qdrant) for similarity — Phase 2 | P2 |

### 6.6 Delivery (Layer 6 — MVP)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-DEL-01 | REST API returning precomputed `published` records only | P0 |
| FR-DEL-02 | Paginated strategic feed with filters (domain, entity, score) | P0 |
| FR-DEL-03 | Health endpoint with ingestion lag metrics | P0 |
| FR-DEL-04 | Slack/Teams/email digest | Out of scope MVP |
| FR-DEL-05 | Website embed | Out of scope MVP |

---

## 7. Intelligence Record Requirements

Every **published** intelligence record MUST include:

| # | Field | Requirement |
|---|-------|-------------|
| 1 | Title | Clear description of change |
| 2 | Summary | Short, concise |
| 3 | Why It Matters | Business impact for Xerago |
| 4 | Domains | ≥1 Xerago domain |
| 5 | Source | Display name + URL + trust tier |
| 6 | Strategic Score | Integer 0–100 |
| 7 | Impact Level | Low \| Medium \| High \| Strategic |
| 8 | Published Date | ISO 8601 |
| 9 | URL | Canonical link |

See `output_schema.md` for full contract.

---

## 8. Signal Quality Requirements

### Must Surface

- Major AI model releases
- New partner capabilities
- Significant gated research breakthroughs
- Important OSS version milestones
- Major ecosystem changes
- Enterprise AI platform announcements
- Material CX innovations

### Must NOT Surface

- Minor bug fixes and routine patches (unless security)
- Marketing fluff
- Duplicates
- Repeated OSS versions
- Low-value trending content
- Unverified rumors without T1 corroboration

---

## 9. Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-01 | **Decoupling** | No synchronous cross-layer dependencies; LLM failure does not delete artifacts |
| NFR-02 | **Precompute** | Zero LLM invocations on API read path |
| NFR-03 | **Event-driven** | Prefer webhooks/queues over blind polling where possible |
| NFR-04 | **Local-first** | Runnable on local infra without mandatory external AI APIs |
| NFR-05 | **Idempotency** | Re-processing same artifact does not duplicate intelligence records |
| NFR-06 | **Auditability** | Promotion trace and score breakdown stored |
| NFR-07 | **Ingestion SLA** | P0 sources: lag < 2 hours (MVP target) |
| NFR-08 | **Enrichment SLA** | Gate-passed artifact → published < 30 minutes (MVP target) |
| NFR-09 | **Security** | Secrets in env/vault; no credentials in repo |

---

## 10. Architecture Constraints

| Constraint | Detail |
|------------|--------|
| Standalone service | Does not replace existing React/Python/TS platform |
| API-first | Website consumes APIs later |
| Tech stack | Python (FastAPI, Celery), MySQL, Redis, FreshRSS; Next.js + TypeScript consumes API in company platform (post-MVP) |
| Existing platform | Integration deferred until validation |

---

## 11. MVP Success Criteria

The MVP is successful when this flow works **reliably**:

```
Article (ingested)
  → Summary (generated)
  → Why It Matters (generated)
  → Strategic Score (computed)
  → Stored intelligence record (published)
  → Retrievable via REST API
```

| Criterion | Measure |
|-----------|---------|
| Pipeline reliability | ≥95% of gate-passed artifacts reach `published` within SLA |
| Intelligence quality | precision@10 ≥ 0.75 (weekly human labels) |
| Noise control | <12% of ingested artifacts become published signals |
| Dedup | <5% duplicate real-world events in top 20 |
| OSS lifecycle | Zero re-surface of same version |
| API | Read-only; no generation on GET |

**First priority:** intelligence quality — not UI, not website integration, not scale-out.

---

## 12. Phased Capabilities (Post-MVP)

| Phase | Capabilities |
|-------|--------------|
| Phase 2 | Feedback loop (useful/not useful), vector search, curator UI |
| Phase 3 | React intelligence UI (standalone) |
| Phase 4 | Website section integration, SSO |
| Phase 5 | Slack/Teams digest, personalization, client-specific views |

See `roadmap.md`.

---

## 13. Dependencies and Risks

| Risk | Mitigation |
|------|------------|
| LLM quality inconsistent | Rules-first gates; template validation; local model tuning |
| RSS/source format drift | Parser alerts; source health dashboard |
| Over-filtering | Weekly calibration with practice leads |
| Under-filtering | Aggressive default thresholds; noise penalties |
| GitHub rate limits | ETag caching; token pool |
| FreshRSS operational burden | Document backup/restore; single-node MVP acceptable |

---

## 14. Acceptance Tests (MVP)

| Test | Expected |
|------|----------|
| Ingest Salesforce blog post | Artifact in store within SLA |
| Duplicate URL re-ingested | Single intelligence record |
| LangGraph v1.0 release | Signal published; ledger updated |
| LangGraph v1.0 re-polled | No new signal |
| LangGraph v1.1 release | New signal published |
| Marketing fluff post | Suppressed; not published |
| Research paper (no gate) | Research store only |
| GET /v1/intelligence | Returns precomputed records only |
| LLM worker down | Artifacts queue; resume without loss |

---

## 15. Documentation Index

| # | Deliverable | Document |
|---|-------------|----------|
| 1 | Source taxonomy | `sources.md` |
| 2 | Category taxonomy | `categories.md` |
| 3 | Signal rules | `signal_rules.md` |
| 4 | Scoring model | `scoring_model.md` |
| 5 | Output schema | `output_schema.md` |
| 6 | Repository tracking | `repository_tracking_strategy.md` |
| 7 | Research intelligence | `research_intelligence_strategy.md` |
| 8 | Strategic signal framework | `strategic_signal_framework.md` |
| 9 | Product requirements | `product_requirements.md` (this document) |
| 10 | MVP roadmap | `roadmap.md` |

---

## 16. Glossary

| Term | Definition |
|------|------------|
| **Signal** | Promoted, scored, enriched intelligence record |
| **Artifact** | Raw ingested content before promotion |
| **Strategic Score** | 0–100 importance metric |
| **Domain** | Xerago business capability tag |
| **Gate** | Rule that blocks or allows promotion |

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-05-29 | Initial PRD aligned to Master Project Context |
