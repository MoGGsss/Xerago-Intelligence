# Source Taxonomy

## Purpose

This document defines the authoritative **source taxonomy and registry** for the Xerago Intelligence Engine—an Enterprise Technology Radar, not a news aggregator.

Sources feed **Layer 1 (Ingestion)** via FreshRSS, GitHub APIs, and research APIs. Events are published to the **event bus (Layer 2)** for async processing. This registry is the single source of truth for provenance, priority, and trust.

---

## Ingestion Architecture Alignment

| Layer | Technology | Role |
|-------|------------|------|
| Ingestion | FreshRSS (RSS/Atom), GitHub API, research APIs | Collect only; no scoring |
| Event bus | Webhooks, Redis, RabbitMQ | Decouple ingest from workers |
| Processing | Python, Celery | Normalize artifacts |

**Local-first:** Run FreshRSS and workers locally; prefer internal LLM endpoints for enrichment.

---

## Source Priority (Business Order)

| Priority | Group | Entities |
|----------|-------|------------|
| **P0** | Partner ecosystem | Adobe, Salesforce, IBM, SAS, Acquia, Acoustic, HCL, Unica |
| **P1** | AI vendors | OpenAI, Google AI, Microsoft AI, Anthropic, HuggingFace |
| **P2** | Open source | Curated repos (`repository_tracking_strategy.md`) |
| **P3** | Research | Stanford AI, Papers With Code |
| **P4** | Industry intelligence | TechCrunch AI, Verge AI, TLDR AI |

P0 sources have highest scoring partner relevance and tightest ingest SLAs.

---

## Source Taxonomy (Types)

| Type | Description | Primary Signal Value |
|------|-------------|----------------------|
| **Partner** | Strategic MarTech/CX/analytics platform vendors | Product releases, AI capabilities, integrations, roadmap |
| **AI Vendor** | Foundation-model and enterprise AI providers | Model releases, agents, APIs, governance |
| **Open Source** | Curated GitHub repositories (lifecycle, not trending) | Version and milestone releases |
| **Research** | Academic and benchmark institutions | Breakthroughs (gated promotion) |
| **Industry** | Curated publishers | Ecosystem narrative; corroboration role |

---

## Trust Tiers

| Tier | Definition | Default Weight in Scoring |
|------|------------|---------------------------|
| **T1 — Primary** | Official channels owned by the entity (blog, docs, GitHub org, press room) | Highest |
| **T2 — Curated** | Reputable third-party aggregators and editorial outlets | Medium |
| **T3 — Secondary** | Community, social, or unverified reposts | Low (ingest only if linked to T1/T2) |

All scored signals must trace to at least one T1 or T2 source. T3 sources may enrich context but must not originate standalone strategic signals.

---

## Partner Sources

### Adobe

| Source ID | Name | URL Pattern | Ingestion | Cadence | Tier |
|-----------|------|-------------|-----------|---------|------|
| `adobe-blog` | Adobe Blog | `blog.adobe.com` | RSS / HTML scrape | 4h | T1 |
| `adobe-product-docs` | Adobe Experience Cloud Docs | `experienceleague.adobe.com` | Docs API / sitemap | 24h | T1 |
| `adobe-github` | Adobe Open Source | `github.com/adobe` | GitHub Releases API | 1h | T1 |
| `adobe-press` | Adobe Newsroom | `news.adobe.com` | RSS | 4h | T1 |

**Tracked domains:** Experience Cloud, Marketo, Analytics, Target, AEM, Firefly, GenStudio

---

### Salesforce

| Source ID | Name | URL Pattern | Ingestion | Cadence | Tier |
|-----------|------|-------------|-----------|---------|------|
| `sf-blog` | Salesforce Blog | `salesforce.com/blog` | RSS | 4h | T1 |
| `sf-release-notes` | Salesforce Release Notes | `help.salesforce.com` | Sitemap / HTML | 24h | T1 |
| `sf-github` | Salesforce GitHub | `github.com/salesforce` | GitHub Releases API | 1h | T1 |
| `sf-trailhead` | Trailhead / Agentforce announcements | `trailhead.salesforce.com` | RSS / HTML | 24h | T1 |

**Tracked domains:** Marketing Cloud, Data Cloud, Agentforce, MuleSoft, Tableau

---

### IBM

| Source ID | Name | URL Pattern | Ingestion | Cadence | Tier |
|-----------|------|-------------|-----------|---------|------|
| `ibm-newsroom` | IBM Newsroom | `newsroom.ibm.com` | RSS | 4h | T1 |
| `ibm-watson-docs` | IBM watsonx / Cloud docs | `cloud.ibm.com/docs` | Sitemap | 24h | T1 |
| `ibm-github` | IBM GitHub | `github.com/IBM` | GitHub Releases API | 1h | T1 |
| `ibm-research` | IBM Research Blog | `research.ibm.com/blog` | RSS | 24h | T1 |

**Tracked domains:** watsonx, Instana, Cloud Pak, Sterling, Unica (legacy overlap)

---

### SAS

| Source ID | Name | URL Pattern | Ingestion | Cadence | Tier |
|-----------|------|-------------|-----------|---------|------|
| `sas-news` | SAS Newsroom | `sas.com/en/news` | RSS / HTML | 4h | T1 |
| `sas-blog` | SAS Blogs | `blogs.sas.com` | RSS | 4h | T1 |
| `sas-github` | SAS GitHub | `github.com/sassoftware` | GitHub Releases API | 1h | T1 |

**Tracked domains:** Viya, Customer Intelligence, Model Manager, AI/ML platform

---

### Acquia

| Source ID | Name | URL Pattern | Ingestion | Cadence | Tier |
|-----------|------|-------------|-----------|---------|------|
| `acquia-blog` | Acquia Blog | `acquia.com/blog` | RSS | 4h | T1 |
| `acquia-product` | Acquia Product Updates | `docs.acquia.com` | Sitemap | 24h | T1 |
| `acquia-github` | Acquia GitHub | `github.com/acquia` | GitHub Releases API | 1h | T1 |

**Tracked domains:** Drupal Cloud, DAM, CDP, personalization

---

### Acoustic

| Source ID | Name | URL Pattern | Ingestion | Cadence | Tier |
|-----------|------|-------------|-----------|---------|------|
| `acoustic-blog` | Acoustic Blog | `acoustic.com/blog` | RSS | 4h | T1 |
| `acoustic-docs` | Acoustic Documentation | `developer.acoustic.com` | Sitemap | 24h | T1 |
| `acoustic-github` | Acoustic GitHub | `github.com/go-acoustic` | GitHub Releases API | 1h | T1 |

**Tracked domains:** Campaign, Connect, Exchange, Tealeaf

---

### HCL

| Source ID | Name | URL Pattern | Ingestion | Cadence | Tier |
|-----------|------|-------------|-----------|---------|------|
| `hcl-news` | HCLTech Newsroom | `hcltech.com/newsroom` | RSS | 4h | T1 |
| `hcl-unica-docs` | HCL Unica / Marketing docs | `help.hcl-software.com` | Sitemap | 24h | T1 |
| `hcl-github` | HCL Software GitHub | `github.com/hcl-tech-software` | GitHub Releases API | 1h | T1 |

**Tracked domains:** Unica, Commerce, DX, BigFix (adjacent)

---

### Unica (HCL Product Line)

Unica is tracked both under HCL corporate sources and as a product-specific watchlist.

| Source ID | Name | URL Pattern | Ingestion | Cadence | Tier |
|-----------|------|-------------|-----------|---------|------|
| `unica-release-notes` | HCL Unica Release Notes | `help.hcl-software.com/unica` | Sitemap / HTML | 24h | T1 |
| `unica-community` | Unica practitioner forums | Community portals | HTML (limited) | 24h | T3 |

---

## AI Company Sources

### OpenAI

| Source ID | Name | Ingestion | Cadence | Tier |
|-----------|------|-----------|---------|------|
| `openai-blog` | OpenAI Blog / News | RSS | 2h | T1 |
| `openai-github` | OpenAI GitHub | GitHub Releases API | 1h | T1 |
| `openai-changelog` | API / platform changelog | HTML / RSS | 4h | T1 |

---

### Google (DeepMind / Google AI)

| Source ID | Name | Ingestion | Cadence | Tier |
|-----------|------|-----------|---------|------|
| `google-ai-blog` | Google AI / DeepMind Blog | RSS | 2h | T1 |
| `google-cloud-ai` | Google Cloud AI announcements | RSS | 4h | T1 |
| `google-github` | google-deepmind, google-gemini orgs | GitHub Releases API | 1h | T1 |

---

### Microsoft

| Source ID | Name | Ingestion | Cadence | Tier |
|-----------|------|-----------|---------|------|
| `ms-ai-blog` | Microsoft AI Blog | RSS | 2h | T1 |
| `ms-azure-openai` | Azure OpenAI / Copilot updates | RSS / docs sitemap | 4h | T1 |
| `ms-github` | Microsoft org releases | GitHub Releases API | 1h | T1 |

---

### Anthropic

| Source ID | Name | Ingestion | Cadence | Tier |
|-----------|------|-----------|---------|------|
| `anthropic-news` | Anthropic News | RSS / HTML | 2h | T1 |
| `anthropic-docs` | Claude docs / API changelog | Sitemap | 4h | T1 |
| `anthropic-github` | Anthropic GitHub | GitHub Releases API | 1h | T1 |

---

### Hugging Face

| Source ID | Name | Ingestion | Cadence | Tier |
|-----------|------|-----------|---------|------|
| `hf-blog` | Hugging Face Blog | RSS | 4h | T1 |
| `hf-papers` | Daily Papers | RSS / API | 4h | T1 |
| `hf-github` | huggingface org | GitHub Releases API | 1h | T1 |
| `hf-model-hub` | Trending models (metadata only) | HF Hub API | 6h | T2 |

---

## Research Sources

### Stanford AI

| Source ID | Name | Ingestion | Cadence | Tier |
|-----------|------|-----------|---------|------|
| `stanford-hai` | Stanford HAI | RSS | 24h | T1 |
| `stanford-ai-index` | AI Index Report (annual + updates) | Manual + RSS alerts | Event-driven | T1 |
| `stanford-snap` | SNAP / relevant labs (selected) | RSS / arXiv author watch | 24h | T2 |

---

### Papers With Code

| Source ID | Name | Ingestion | Cadence | Tier |
|-----------|------|-----------|---------|------|
| `pwc-trending` | Trending papers | PWC API / RSS | 6h | T2 |
| `pwc-benchmarks` | State-of-the-art benchmark shifts | PWC API | 12h | T2 |
| `pwc-datasets` | New benchmark datasets | PWC API | 24h | T3 |

Research signals require a **relevance gate** (see `signal_rules.md`) before entering the strategic feed.

---

## Industry Sources

### TechCrunch AI

| Source ID | Name | Ingestion | Cadence | Tier |
|-----------|------|-----------|---------|------|
| `tc-ai` | TechCrunch AI category | RSS (filtered) | 2h | T2 |

**Filter:** Tag/category = AI, enterprise SaaS, MarTech, or named partner entities.

---

### The Verge AI

| Source ID | Name | Ingestion | Cadence | Tier |
|-----------|------|-----------|---------|------|
| `verge-ai` | The Verge AI section | RSS | 2h | T2 |

---

### TLDR AI

| Source ID | Name | Ingestion | Cadence | Tier |
|-----------|------|-----------|---------|------|
| `tldr-ai` | TLDR AI newsletter | Email parse / RSS mirror | 24h | T2 |

Industry sources are **narrative amplifiers**. They may elevate an existing signal's velocity score but should not create net-new partner signals without T1 corroboration.

---

## Cross-Cutting Source: GitHub Releases

GitHub is a first-class ingestion channel across partners and AI companies.

| Capability | Scope |
|------------|-------|
| Release events | Tags, release notes, asset metadata |
| Repo watchlist | Curated per entity in source registry |
| Signal types | Major version, breaking change keywords, security advisories |

See `signal_rules.md` for release classification rules.

---

## Source Metadata Schema (Registry Record)

Each source record in the operational registry includes:

```
source_id          — Unique identifier (stable, kebab-case)
entity             — Adobe | Salesforce | … | Industry
source_type        — blog | docs | github | rss | api | newsletter
base_url           — Canonical origin
ingestion_method   — pull_rss | pull_api | scrape | webhook
refresh_cadence    — ISO 8601 duration or cron
trust_tier         — T1 | T2 | T3
enabled            — boolean
rate_limit_policy  — requests per minute
last_successful_run — timestamp
failure_count      — integer (circuit breaker input)
tags               — [product-line, geography, …]
```

---

## Ingestion Principles

1. **Provenance first** — Every raw artifact stores `source_id`, fetch timestamp, and canonical URL.
2. **Fail gracefully** — Source failures degrade per-source, not platform-wide.
3. **Respect robots and ToS** — Prefer RSS/API over scrape; cache aggressively.
4. **Normalize early** — Map all inputs to a common raw document envelope before classification.
5. **Entity linking** — Attach one or more `entity` tags at ingestion based on source registry defaults plus content inference.

---

## Source Expansion Process

New sources enter through a governed workflow:

1. **Proposal** — Business justification and entity mapping
2. **Technical review** — Ingestion feasibility, rate limits, legal/ToS
3. **Pilot** — 2-week ingest-only (no scoring surfacing)
4. **Promotion** — Assign trust tier and scoring weight
5. **Registry commit** — Version-controlled update to this document and operational config

---

## Out of Scope (Initial Phase)

| Excluded | Rationale |
|----------|-----------|
| Social media firehoses (X, LinkedIn) | High noise; revisit in Phase 3 with strict filters |
| Paid analyst reports (Gartner, Forrester) | Licensing; manual upload path in future |
| Client-specific internal systems | Separate tenant layer; not global intelligence |
| Broad web search | Unbounded scope; conflicts with noise-reduction goal |

---

## Related Documents

- `categories.md` — How ingested content is classified
- `signal_rules.md` — Promotion from raw artifact to signal
- `scoring_model.md` — Ranking surfaced signals
- `output_schema.md` — Consumer-facing payload structure
