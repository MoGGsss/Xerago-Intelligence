# Output Schema Specification

## Purpose

Defines the **Intelligence Record** contract—the precomputed artifact stored in **MySQL** and returned by the **FastAPI** REST layer. The **Next.js + React + TypeScript** company platform (post-MVP) and other clients are **read-only consumers**.

**MVP principle:** APIs never trigger LLM generation. Missing enrichment = record not yet ready (404 or `status: processing`).

---

## Intelligence Record (Canonical)

Every stored signal conforms to this schema.

```json
{
  "intelligence_id": "intel_01JABC1234567890",
  "status": "published",
  "title": "Salesforce expands autonomous journey orchestration",
  "summary": "Salesforce introduced new autonomous customer journey orchestration capabilities within Marketing Cloud, enabling AI-driven decisioning across channels.",
  "why_it_matters": "This may accelerate enterprise adoption of AI-driven marketing automation and customer experience optimization. Xerago clients using Marketing Cloud should assess journey design and data readiness for autonomous orchestration.",
  "domains": [
    {
      "slug": "customer-experience",
      "display_name": "Customer Experience",
      "is_primary": true
    },
    {
      "slug": "martech",
      "display_name": "Martech",
      "is_primary": false
    }
  ],
  "event_type": {
    "primary": "product-technology",
    "subcategory": "feature-addition",
    "labels": {
      "primary": "Product & Technology",
      "subcategory": "Feature Addition"
    }
  },
  "entity": {
    "primary": "Salesforce",
    "group": "partner"
  },
  "source": {
    "source_id": "sf-blog",
    "display_name": "Salesforce",
    "trust_tier": "T1",
    "url": "https://www.salesforce.com/blog/..."
  },
  "strategic_score": 91,
  "impact_level": "High",
  "employee_relevance": "practice",
  "published_at": "2026-05-28T14:00:00Z",
  "ingested_at": "2026-05-28T14:15:00Z",
  "enriched_at": "2026-05-28T14:20:00Z",
  "scoring_version": "scoring_v2.0.0",
  "score_breakdown": {
    "xerago_relevance": { "value": 0.90, "contribution": 0.20 },
    "partner_relevance": { "value": 1.00, "contribution": 0.20 },
    "enterprise_applicability": { "value": 0.88, "contribution": 0.16 },
    "innovation_level": { "value": 0.75, "contribution": 0.11 },
    "source_trust": { "value": 1.00, "contribution": 0.12 },
    "recency": { "value": 0.92, "contribution": 0.09 },
    "noise_penalty": { "value": 0.00, "contribution": 0.00 }
  }
}
```

---

## Required Fields (MVP)

| Field | Type | Constraint |
|-------|------|------------|
| `intelligence_id` | string | `intel_` + ULID |
| `status` | enum | `processing` \| `published` \| `suppressed` |
| `title` | string | ≤ 300 chars |
| `summary` | string | ≤ 600 chars (~120 words) |
| `why_it_matters` | string | ≤ 1000 chars; required when `status=published` |
| `domains` | array | 1–4 items; exactly one `is_primary: true` |
| `source` | object | `display_name`, `url`, `trust_tier` |
| `strategic_score` | integer | 0–100 |
| `impact_level` | enum | Low \| Medium \| High \| Strategic |
| `published_at` | ISO8601 UTC | — |
| `source.url` | URI | Canonical article or release URL |

---

## Optional Fields

| Field | When Present |
|-------|--------------|
| `event_type` | Always after classification |
| `entity` | When entity identified |
| `employee_relevance` | After scoring |
| `score_breakdown` | After scoring |
| `cluster_id` | When deduplicated cluster exists |
| `related_sources[]` | Detail view; corroborating URLs |
| `github` | OSS release signals |
| `research` | Promoted research signals |
| `promotion_trace[]` | Detail view; audit rule IDs |
| `product_tags[]` | Fine-grained product names |

---

## Status Lifecycle

```
processing → published
processing → suppressed (failed gates; audit only)
published  → suppressed (manual curator; rare)
```

Clients polling MVP API should treat `processing` as not yet available for user display.

---

## GitHub Extension

```json
{
  "github": {
    "repo_id": "langchain-ai/langgraph",
    "release_tag": "v1.1.0",
    "semver": { "major": 1, "minor": 1, "patch": 0 },
    "release_url": "https://github.com/langchain-ai/langgraph/releases/tag/v1.1.0",
    "previous_surfaced_version": "v1.0.0",
    "tier": "A"
  }
}
```

---

## Research Extension

```json
{
  "research": {
    "paper_title": "Example Paper Title",
    "arxiv_id": "2605.12345",
    "benchmarks": ["SWE-bench"],
    "gate_rule": "RI-GATE-002",
    "pwc_url": "https://paperswithcode.com/..."
  }
}
```

---

## API Surface (MVP)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/intelligence` | GET | Paginated strategic feed (`status=published`) |
| `/v1/intelligence/{id}` | GET | Single record |
| `/v1/intelligence/feed/partner` | GET | Partner ecosystem feed |
| `/v1/health` | GET | Service + ingestion freshness |

**Not in MVP:** Frontend-specific BFF, Slack, Teams, website embed.

### Query Parameters — `GET /v1/intelligence`

| Param | Type | Default |
|-------|------|---------|
| `min_score` | int | 55 |
| `domain` | slug | — |
| `entity` | string | — |
| `impact_level` | enum | — |
| `since` | ISO8601 | 7 days ago |
| `limit` | int | 20 (max 50) |
| `cursor` | string | — |

---

## Feed Response Envelope

```json
{
  "feed": "strategic-top",
  "generated_at": "2026-05-29T08:00:00Z",
  "precomputed": true,
  "pagination": {
    "cursor": null,
    "next_cursor": "eyJwIjoyfQ",
    "limit": 20
  },
  "intelligence": []
}
```

---

## Error Responses

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Intelligence record not found or still processing",
    "request_id": "req_01JXYZ"
  }
}
```

| HTTP | Code | When |
|------|------|------|
| 404 | `NOT_FOUND` | Unknown ID or still `processing` |
| 400 | `INVALID_FILTER` | Bad query param |
| 503 | `FEED_STALE` | Ingestion lag exceeds SLA |

---

## Mapping to User-Facing Example

| User Example Field | Schema Field |
|--------------------|--------------|
| Title | `title` |
| Summary | `summary` |
| Why It Matters | `why_it_matters` |
| Categories | `domains[].display_name` |
| Source | `source.display_name` |
| Strategic Score | `strategic_score` |
| Impact | `impact_level` |
| Published Date | `published_at` |
| URL | `source.url` |

---

## Versioning Headers

| Header | Example |
|--------|---------|
| `X-Schema-Version` | `2026-05-29` |
| `X-Scoring-Version` | `scoring_v2.0.0` |
| `X-Domains-Version` | `domains_v1.0.0` |

---

## Precompute Contract

| Operation | When |
|-----------|------|
| Ingest artifact | Layer 1 (sync to store) |
| Classify + dedupe | Layer 3 worker |
| Score | Layer 4 worker |
| Summarize + why-it-matters | Layer 3 worker (after gate pass) |
| Set `status=published` | After all required fields populated |

API read path: **SELECT only**. No worker triggers from GET.

---

## Related Documents

- `scoring_model.md` — Score and impact derivation
- `signal_rules.md` — Promotion before publish
- `categories.md` — Domain and event type enums
- `product_requirements.md` — MVP acceptance criteria
