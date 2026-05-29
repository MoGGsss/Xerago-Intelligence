# MVP Roadmap

## Purpose

Phased delivery plan for the Xerago Intelligence Engine, aligned to **standalone service first**, **intelligence quality over UI**, and **local-first** operation. Website and dashboard integration are explicitly deferred.

---

## North Star (MVP)

```
Article → Summary → Why It Matters → Strategic Score → Stored → API
```

**Success = reliable intelligence pipeline**, not frontend polish.

---

## Delivery Phases

| Phase | Name | Duration | Focus |
|-------|------|----------|-------|
| **M0** | Architecture & Registry | 1–2 weeks | Documentation, schemas, source/repo registry |
| **M1** | Ingest & Bus | 2–3 weeks | FreshRSS, GitHub poll, event bus, artifact store |
| **M2** | Processing & Gates | 3–4 weeks | Rules, dedup, OSS ledger, research gate |
| **M3** | Enrichment & Scoring | 2–3 weeks | LLM summary, why-it-matters, strategic score |
| **M4** | API & Validation | 1–2 weeks | REST API, calibration, MVP sign-off |
| — | *Post-MVP* | — | UI, website, digests, feedback loop |

**MVP calendar estimate:** 9–14 weeks (single team, local-first).

---

## M0 — Architecture & Registry

### Outcomes

- Complete architecture documentation set (10 deliverables)
- Machine-readable source registry export
- Initial OSS Tier A watchlist (≥10 repos)
- JSON schema validation for intelligence records
- Docker Compose skeleton (MySQL, Redis, FreshRSS) — config only, no app code required in doc phase

### Exit Criteria

- [ ] Practice lead sign-off on domains, scoring weights, and P0 sources
- [ ] Sample fixture records validate against `output_schema.md`

### Not in scope

- Application code
- Production deployment

---

## M1 — Ingest & Event Bus

### Outcomes

| Component | Deliverable |
|-----------|-------------|
| FreshRSS | P0 partner feeds + P1 AI vendor feeds configured |
| GitHub poller | Tier A repos; ETag-aware |
| Event bus | Redis or RabbitMQ; `artifact.ingested` event |
| Artifact store | MySQL `artifacts` table |
| Health | Per-source last-run and lag in `/v1/health` |

### Source Waves

| Wave | Sources |
|------|---------|
| Wave 1 (M1) | Adobe, Salesforce, IBM — blog/RSS; OpenAI, Anthropic — blog |
| Wave 2 (M1 end) | Remaining partners; Google AI, Microsoft AI; TLDR AI |
| Wave 3 (M2) | Industry (TC, Verge); research; HuggingFace |

### Exit Criteria

- [ ] ≥90% P0 sources ingesting; lag < 2h
- [ ] Artifacts persisted with provenance
- [ ] Ingest continues when processing workers are stopped

---

## M2 — Processing & Gates

### Outcomes

| Capability | Reference |
|------------|-----------|
| Eligibility + classification | `signal_rules.md` |
| Domain mapping | `categories.md` |
| Dedup clustering | `signal_rules.md` |
| OSS version ledger | `repository_tracking_strategy.md` |
| Research store + gate | `research_intelligence_strategy.md` |
| Celery workers | classify, dedupe, gate tasks |

### Exit Criteria

- [ ] <5% duplicate real-world events in processing output
- [ ] OSS: v1.0 surfaced once; re-poll does not re-surface
- [ ] Research: ≥90% papers remain in research store only
- [ ] Promotion trace stored on every candidate signal

---

## M3 — Enrichment & Strategic Scoring

### Outcomes

| Capability | Reference |
|------------|-----------|
| Async summary generation | Local Ollama or internal LLM |
| Why It Matters generation | `product_requirements.md` FR-ENR-02 |
| Strategic score 0–100 | `scoring_model.md` |
| Impact level + employee relevance | `scoring_model.md` |
| Intelligence store | `status: published` records |

### Exit Criteria

- [ ] Gate-passed artifacts reach `published` ≥95% within 30 min
- [ ] Every published record has all 9 required fields
- [ ] strategic_score correlates with human labels (Spearman ≥ 0.6 pilot)
- [ ] LLM outage: artifacts re-queue; no data loss

---

## M4 — API & MVP Validation

### Outcomes

| Endpoint | Behavior |
|----------|----------|
| `GET /v1/intelligence` | Precomputed feed; `min_score` default 55 |
| `GET /v1/intelligence/{id}` | Detail with score breakdown |
| `GET /v1/health` | Ingestion + worker status |

### Validation Activities

| Activity | Duration |
|----------|----------|
| Internal pilot (API consumers) | 2 weeks |
| Weekly calibration labeling | Ongoing |
| Threshold tuning | End of M4 |

### MVP Sign-Off Checklist

- [ ] End-to-end pipeline demonstrated for partner, AI, OSS, and gated research
- [ ] precision@10 ≥ 0.75
- [ ] Ingested → published ratio 5–12%
- [ ] PRD acceptance tests pass (`product_requirements.md` §14)
- [ ] Runbook for local deployment documented

---

## Post-MVP Roadmap

### Phase A — Feedback & Search (4–6 weeks)

- User feedback: useful / not useful / more like this / ignore similar
- FAISS/Qdrant embedding index for similarity suppression and search
- Curator hold-queue UI (internal, minimal)

### Phase B — Standalone UI (4–6 weeks)

- React app: strategic feed, detail, domain filter
- Still separate from company website
- Read-only API client

### Phase C — Website Integration (3–4 weeks)

- Embed intelligence section in existing React platform
- SSO alignment with company auth
- CDN caching for feed endpoint

### Phase D — Distribution (ongoing)

- Slack / Teams weekly digest
- Email digest by domain
- Webhook `intelligence.published` for high-score events

---

## Architecture Milestone Map

```
M0 ──► Registry + docs
M1 ──► Layer 1–2 (Ingest + Bus)
M2 ──► Layer 3 (Processing)
M3 ──► Layer 3–4 (Enrich + Score) + Layer 5 (Store)
M4 ──► Layer 6 (REST API) + Validation
```

---

## Team & Responsibilities

| Role | MVP Focus |
|------|-----------|
| Principal Architect | Taxonomy, scoring, gates, sign-off |
| Backend Engineer | Ingestion, workers, API, database |
| Practice Lead (20%) | Weekly labeling and threshold approval |
| DevOps (10%) | Local Compose, backups, monitoring |

**No dedicated frontend engineer until Phase B.**

---

## Explicitly Deferred

| Item | Earliest Phase |
|------|----------------|
| Company website integration | Phase C |
| React dashboard | Phase B |
| Slack/Teams/email | Phase D |
| Multi-tenant client views | Phase D+ |
| External OpenAI dependency as default | Avoid; internal/local preferred |
| arXiv broad crawl | Phase A+ |

---

## Risk Register (MVP)

| Risk | Phase | Mitigation |
|------|-------|------------|
| FreshRSS ops | M1 | Backup feeds; export OPML |
| Over-filtering | M3–M4 | Calibration loop |
| LLM hallucination in why-it-matters | M3 | Evidence spans; template checks |
| Scope creep to UI | All | PRD non-goals enforced |

---

## Related Documents

- `product_requirements.md` — Requirements and acceptance tests
- `strategic_signal_framework.md` — Platform philosophy
- All taxonomy and rules documents in `docs/`
