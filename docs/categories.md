# Category Taxonomy

## Purpose

This document defines **two orthogonal taxonomies** used by the Xerago Intelligence Engine:

1. **Xerago Domains** — Which business capabilities are affected (required on every intelligence record)
2. **Signal Event Types** — What kind of change occurred (exactly one primary type per signal)

Domains answer *"Who at Xerago should care?"* Event types answer *"What happened?"*

---

## Part 1: Xerago Domain Taxonomy

Every intelligence record maps to **one or more** Xerago domains. Domains drive filtering, digest routing, and the **Xerago Relevance** scoring factor.

### Domain Registry

| Slug | Display Name | Description | Typical Sources |
|------|--------------|-------------|-----------------|
| `ai-ml` | AI & Machine Learning | Models, training, inference, ML platforms | AI vendors, research, OSS |
| `customer-experience` | Customer Experience | CX platforms, journey, service, loyalty | Partners, industry |
| `martech` | Martech | Campaign, email, marketing automation, CDP | Partners (Adobe, SF, Acoustic) |
| `analytics` | Analytics | Measurement, attribution, reporting, BI | Partners, SAS, research |
| `personalization` | Personalization | Targeting, recommendations, decisioning | Adobe, Salesforce, Acquia |
| `automation` | Automation | Workflows, agents, orchestration, RPA | AI vendors, OSS (LangGraph) |
| `enterprise-ai` | Enterprise AI | Governance, deployment, enterprise AI platforms | IBM, Microsoft, OpenAI |
| `open-source-ecosystem` | Open Source Ecosystem | Curated OSS releases and milestones | GitHub registry |
| `research-signals` | Research Signals | Promoted research breakthroughs | Stanford, PWC |
| `industry-trends` | Industry Trends | Market narrative, funding, macro shifts | TechCrunch, Verge, TLDR |
| `cloud-platforms` | Cloud Platforms | Cloud infra, multi-cloud, managed services | IBM, Microsoft, Google |
| `data-engineering` | Data Engineering | Pipelines, lakes, governance, integration | Partners, research |

### Domain Mapping Rules

| Rule ID | Logic |
|---------|-------|
| `DOM-001` | Minimum **1** domain per intelligence record |
| `DOM-002` | Maximum **4** domains (force focus; rank by relevance score) |
| `DOM-003` | Primary domain = highest domain relevance score |
| `DOM-004` | Registry defaults apply for OSS repos (see `repository_tracking_strategy.md`) |
| `DOM-005` | Industry-only narrative → must include `industry-trends` |
| `DOM-006` | Promoted research → must include `research-signals` plus practice domain |

### Domain Inference (Processing Layer)

```
1. Source registry default domains
2. Keyword / product-line dictionary
3. LLM assist (bounded): suggest domains; rules validate
4. Human curator override (Phase 2)
```

### Example Mapping

| Signal | Domains |
|--------|---------|
| Salesforce autonomous journey orchestration | `customer-experience`, `martech` |
| LangGraph v1.1 release | `automation`, `open-source-ecosystem`, `ai-ml` |
| OpenAI enterprise API pricing change | `enterprise-ai`, `ai-ml` |
| Stanford AI Index annual report | `research-signals`, `enterprise-ai`, `industry-trends` |

---

## Part 2: Signal Event Type Taxonomy

Event types classify the **nature of the change**. Exactly **one** primary L1 and **one** L2 subcategory per signal.

### L1 Overview

```
event/
├── product-technology
├── go-to-market
├── partnership-ecosystem
├── research-innovation
├── regulatory-trust
├── competitive-landscape
├── operational-incident
└── market-narrative
```

### L1: `product-technology`

| Attribute | Value |
|-----------|-------|
| Default score modifier | High |
| Typical domains | Varies by product |

| L2 Slug | Description |
|---------|-------------|
| `major-release` | GA or major version |
| `feature-addition` | New capability |
| `api-platform` | API/SDK change |
| `deprecation-eol` | Sunset or breaking removal |
| `performance-scale` | Measurable perf/cost improvement |
| `security-patch` | Security fix requiring action |
| `open-source` | OSS release (see repository strategy) |

---

### L1: `go-to-market`

| L2 Slug | Description |
|---------|-------------|
| `pricing-change` | Price or token economics |
| `packaging-sku` | Bundle/tier change |
| `licensing-terms` | Usage or contract terms |
| `availability-geo` | Regional availability |
| `sales-program` | Partner/marketplace program |

---

### L1: `partnership-ecosystem`

| L2 Slug | Description |
|---------|-------------|
| `strategic-alliance` | Deep partnership |
| `integration-connector` | Certified integration |
| `acquisition` | M&A |
| `divestiture` | Spin-off or sale |
| `investment` | Minority stake / fund |
| `isv-marketplace` | Marketplace policy or listing |

---

### L1: `research-innovation`

| L2 Slug | Description |
|---------|-------------|
| `foundation-model` | Architecture / training advance |
| `benchmark-sota` | Leaderboard shift |
| `applied-enterprise` | Enterprise-applicable research |
| `safety-alignment` | Safety / alignment research |
| `hardware-efficiency` | Compute efficiency |
| `annual-report` | AI Index, industry survey |

**Note:** Requires research relevance gate. See `research_intelligence_strategy.md`.

---

### L1: `regulatory-trust`

| L2 Slug | Description |
|---------|-------------|
| `ai-regulation` | AI-specific regulation |
| `data-privacy` | Privacy and consent |
| `trust-safety-policy` | Usage or behavior policy |
| `certification-audit` | Compliance certification |
| `litigation-enforcement` | Legal action |

---

### L1: `competitive-landscape`

| L2 Slug | Description |
|---------|-------------|
| `market-share` | Share or ranking data |
| `competitive-win-loss` | Displacement narrative |
| `positioning-shift` | Category creation/rebrand |
| `talent-executive` | Strategic hire/departure |

---

### L1: `operational-incident`

| L2 Slug | Description |
|---------|-------------|
| `outage-degradation` | Active incident |
| `data-breach` | Confirmed breach |
| `critical-bug` | Widespread defect |
| `incident-resolved` | Resolution / postmortem |

---

### L1: `market-narrative`

| L2 Slug | Description |
|---------|-------------|
| `funding-valuation` | Startup funding |
| `thought-leadership` | Opinion / prediction |
| `macro-trend` | Industry-wide trend piece |
| `rumor-unconfirmed` | Unverified leak |

**Rule:** `rumor-unconfirmed` cannot enter strategic feed without T1 corroboration.

---

## Cross-Reference: Event Type → Typical Domains

| Event L1 | Common Domains |
|----------|----------------|
| product-technology (partner) | `martech`, `customer-experience`, `analytics`, `personalization` |
| product-technology (AI vendor) | `enterprise-ai`, `ai-ml`, `automation` |
| product-technology (OSS) | `open-source-ecosystem`, `automation`, `ai-ml` |
| go-to-market | `martech`, `enterprise-ai`, `cloud-platforms` |
| research-innovation | `research-signals`, `ai-ml`, `enterprise-ai` |
| market-narrative | `industry-trends` |

---

## Entity Dimension (Watchlist)

Orthogonal to domains and event types. Every signal tags **≥1 entity**:

| Group | Entities |
|-------|----------|
| Partners (P0) | Adobe, Salesforce, IBM, SAS, Acquia, Acoustic, HCL, Unica |
| AI Vendors (P1) | OpenAI, Google AI, Microsoft AI, Anthropic, HuggingFace |
| Research (P3) | Stanford AI, Papers With Code |
| Industry (P4) | TechCrunch AI, Verge AI, TLDR AI |

---

## Product Line Tags (Optional)

Fine-grained tags for consultants: Agentforce, Marketo, Firefly, watsonx, Unica Campaign, etc. Not a substitute for domains.

---

## Versioning

| Artifact | Version |
|----------|---------|
| Domain taxonomy | `domains_v1.0.0` |
| Event taxonomy | `taxonomy_v1.0.0` |

Breaking changes require 90-day slug aliases.

---

## Related Documents

- `strategic_signal_framework.md` — Dual taxonomy rationale
- `scoring_model.md` — Domain-based Xerago relevance factor
- `output_schema.md` — `domains[]` and `event_type` fields
- `signal_rules.md` — Classification rules
