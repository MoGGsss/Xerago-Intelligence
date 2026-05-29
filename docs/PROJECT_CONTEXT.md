# Xerago Intelligence Engine — Master Project Context

## Project Overview

We are building an **Enterprise Intelligence Engine** for Xerago.

This is **NOT** a news aggregator.  
This is **NOT** an RSS reader.  
This is **NOT** a simple AI summarization tool.

The goal is to create an **Enterprise Technology Radar and Strategic Intelligence Platform** that continuously monitors partner ecosystems, AI vendors, research communities, open-source ecosystems, and industry news sources and converts them into **actionable business intelligence**.

The system should answer:

- What changed?
- Why does it matter?
- Which Xerago domains are affected?
- How important is this update?
- Should employees care about it?

**Objective:** Maximize signal quality while minimizing noise.

---

## Existing Environment

The company has a production web application (React frontend; Python + TypeScript backend). The Intelligence Engine **does not replace** it. Build standalone → validate → integrate later into a website section. **Frontend integration is not the current focus.**

---

## Architecture Documentation Index

| # | Deliverable | Document |
|---|-------------|----------|
| 1 | Source taxonomy | [`sources.md`](sources.md) · [`registry/sources.yaml`](../registry/sources.yaml) |
| 2 | Category taxonomy | [`categories.md`](categories.md) |
| 3 | Signal rules | [`signal_rules.md`](signal_rules.md) |
| 4 | Scoring model | [`scoring_model.md`](scoring_model.md) |
| 5 | Output schema | [`output_schema.md`](output_schema.md) |
| 6 | Repository tracking strategy | [`repository_tracking_strategy.md`](repository_tracking_strategy.md) · [`registry/repos.yaml`](../registry/repos.yaml) |
| 7 | Research intelligence strategy | [`research_intelligence_strategy.md`](research_intelligence_strategy.md) |
| 8 | Strategic signal framework | [`strategic_signal_framework.md`](strategic_signal_framework.md) |
| 9 | Product requirements | [`product_requirements.md`](product_requirements.md) |
| 10 | MVP roadmap | [`roadmap.md`](roadmap.md) |

**Machine-readable registries:** `registry/schemas/sources.schema.json`, `registry/schemas/repos.schema.json`

## MVP Implementation Planning

| Document | Path |
|----------|------|
| Overview | [`docs/implementation/README.md`](implementation/README.md) |
| Project structure | [`docs/implementation/project-structure.md`](implementation/project-structure.md) |
| Service boundaries | [`docs/implementation/service-boundaries.md`](implementation/service-boundaries.md) |
| Implementation order | [`docs/implementation/mvp-implementation-order.md`](implementation/mvp-implementation-order.md) |
| Database schema | [`db/schema/001_initial.sql`](../db/schema/001_initial.sql) |

---

## High-Level Pipeline

1. Collect information  
2. Filter irrelevant content  
3. Generate AI summaries  
4. Generate "Why It Matters"  
5. Detect strategic signals  
6. Remove duplicates  
7. Score importance  
8. Deliver intelligence (API; digests later)

---

## Sources To Track

**Partners (P0):** Adobe, Salesforce, IBM, SAS, Acquia, Acoustic, HCL, Unica  

**AI Vendors (P1):** OpenAI, Google AI, Microsoft AI, Anthropic, HuggingFace  

**Research (P3):** Stanford AI, Papers With Code  

**Industry (P4):** TechCrunch AI, Verge AI, TLDR AI  

**Open Source (P2):** Curated GitHub repos — lifecycle monitoring, not trending.

---

## Xerago Domains

AI & Machine Learning · Customer Experience · Martech · Analytics · Personalization · Automation · Enterprise AI · Open Source Ecosystem · Research Signals · Industry Trends · Cloud Platforms · Data Engineering

---

## MVP Success Criteria

```
Article → Summary → Why It Matters → Strategic Score → Stored Result
```

First goal: **intelligence quality** — not UI, not dashboard integration, not enterprise scaling.

---

## Architecture Principles

- **Decoupled** — Async layers; no data loss on LLM/API failure  
- **Precompute everything** — No generation on frontend requests  
- **Event-driven** — Webhooks, queues, workers  
- **Local-first** — FreshRSS, MySQL, Redis, Ollama / internal LLM  
- **Integration target** — Next.js + React + TypeScript (existing company platform); Python remains the processing engine  
- **Feedback loop (future)** — Useful / Not useful / More like this / Ignore similar

---

## Proposed Stack (Layers 1–6)

| Layer | Technology |
|-------|------------|
| Ingestion | FreshRSS, GitHub API, research APIs |
| Event bus | Webhooks, Redis, RabbitMQ |
| Processing | Python, FastAPI, Celery |
| Strategic signal engine | Scoring, impact, employee relevance |
| Storage | MySQL, Redis, FAISS/Qdrant (later) |
| Delivery | FastAPI REST (MVP); Next.js UI (company app, post-MVP); Slack/Teams/email later |
