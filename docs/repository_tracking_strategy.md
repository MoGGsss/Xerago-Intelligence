# Repository Tracking Strategy

## Purpose

This document defines how the Xerago Intelligence Engine monitors **open-source repositories** through a **lifecycle model**—not a trending or popularity model.

The goal is to detect **meaningful version and milestone changes** that affect Xerago delivery, integrations, and client solutions. The system must **not** re-surface a repository simply because it remains popular or receives routine commits.

---

## Core Principle

```
Lifecycle Monitoring  ≠  Trending Monitoring
```

| Lifecycle Model | Trending Model (Rejected) |
|-----------------|---------------------------|
| Track curated repo list | Track GitHub trending |
| Surface on version/milestone | Surface on star count spike |
| Remember last surfaced version | Forget after each poll |
| Ignore commit noise | Surface on activity volume |

---

## Repository Registry

Each tracked repository is a governed registry record:

| Field | Description |
|-------|-------------|
| `repo_id` | Stable ID: `org/repo` (lowercase) |
| `display_name` | Human label |
| `entity` | Linked partner/AI vendor or `ecosystem` |
| `domains[]` | Xerago domains (see `categories.md`) |
| `track_releases` | boolean — monitor GitHub Releases |
| `track_tags` | boolean — monitor annotated tags if no releases |
| `semver_policy` | Which version bumps promote signals |
| `milestone_keywords` | Optional: `security`, `breaking`, `GA`, `LTS` |
| `priority` | P0 (critical) \| P1 \| P2 |
| `enabled` | boolean |
| `last_surfaced_version` | Last version that became a signal |
| `last_surfaced_at` | Timestamp of last promotion |
| `notes` | Curator rationale |

---

## Repository Tiers

### Tier A — Strategic (P0)

Repositories directly tied to Xerago delivery stacks and partner implementations.

| Category | Examples (Illustrative) |
|----------|-------------------------|
| Agent / orchestration frameworks | `langchain-ai/langgraph`, `microsoft/autogen` |
| Partner SDKs and connectors | Org repos under Salesforce, Adobe, IBM |
| Enterprise AI runtimes | `vllm-project/vllm`, inference stacks used in proposals |
| CDP / analytics OSS adjacency | Curated per practice lead approval |

**Promotion policy:** Major and minor semver releases; security releases; documented breaking changes on any bump.

### Tier B — Ecosystem (P1)

Important but not daily consulting dependencies.

| Category | Examples |
|----------|----------|
| Hugging Face core libraries | `huggingface/transformers` |
| Evaluation / RAG tooling | Selected benchmark and eval repos |
| MarTech open components | Drupal modules, connector frameworks |

**Promotion policy:** Major semver; minor if release notes contain `breaking`, `API`, `deprecated`, `security`.

### Tier C — Watch (P2)

Tracked for situational awareness; strict promotion bar.

**Promotion policy:** Major semver only, or explicit security/CVE advisory.

---

## Version Ledger (Anti-Repeat Mechanism)

Every repository maintains a **version ledger** in MySQL:

```
repo_id | version | surfaced_signal_id | surfaced_at
```

### Resurface Rules

| Condition | Action |
|-----------|--------|
| New `version` not in ledger | Evaluate for promotion |
| Same `version` already in ledger | **Suppress** — do not create signal |
| No new release/tag since last poll | **No artifact, no signal** |
| Pre-release (`alpha`, `beta`, `rc`) | Hold unless Tier A + breaking/security |

### LangGraph Example (Required Behavior)

| Event | System Behavior |
|-------|-----------------|
| LangGraph **v1.0** released | Promote → signal created → ledger `v1.0` |
| Daily commits, no new tag | **Ignore** |
| LangGraph **v1.1** released | Promote → new signal → ledger `v1.1` |
| v1.1 re-ingested (duplicate webhook) | Dedup by `repo_id + version` → suppress |

---

## Ingestion Mechanics

### Preferred: GitHub Releases API

```
GET /repos/{org}/{repo}/releases
```

Poll cadence:

| Tier | Cadence |
|------|---------|
| P0 | Every 1 hour |
| P1 | Every 4 hours |
| P2 | Every 12 hours |

Use `ETag` / `If-Modified-Since` to minimize calls. Emit event to bus only when **new release ID** detected.

### Fallback: Tags API

When releases are not used:

```
GET /repos/{org}/{repo}/tags
```

Compare semver of latest tag vs. `last_surfaced_version`.

### Not Used

| Mechanism | Reason |
|-----------|--------|
| GitHub Trending API | Violates lifecycle philosophy |
| Star/watch counts | Not a signal |
| Commit stream | Extreme noise |
| PR merge events | Unless tagged release follows |

---

## Event → Signal Pipeline (OSS-Specific)

```
GitHub webhook or poll
    → Normalize release event
    → Match repo_id in registry
    → Version ledger check (DEDUP-OSS-001)
    → Semver policy check (CLS-PT-OSS-*)
    → Classify: product-technology / open-source
    → Map Xerago domains from registry defaults
    → Score (boost for Tier A major)
    → Enrich (summary + why-it-matters)
    → Write ledger + intelligence record
```

---

## Semver Promotion Matrix

| Change | Tier A | Tier B | Tier C |
|--------|--------|--------|--------|
| Major (`X.0.0`) | Promote | Promote | Promote |
| Minor (`0.X.0`) | Promote | Promote if keywords | Hold |
| Patch (`0.0.X`) | Promote if security/breaking | Promote if security only | Promote if security only |
| Non-semver tag | Hold unless milestone keyword | Hold | Hold |

---

## Release Notes Analysis

When release body is present:

| Pattern | Effect |
|---------|--------|
| `BREAKING CHANGE` / `breaking` | Force promote (if not ledger dup) |
| `CVE-`, `security fix` | Force promote; impact ≥ High |
| `deprecated` | Promote; impact High for Tier A |
| Marketing-only body (< 50 chars technical content) | Hold for enrichment review |

LLM enrichment may extract impact; rules engine has final promotion authority.

---

## Relationship to Partner GitHub Orgs

Partner org repos (Adobe, Salesforce, IBM, etc.) follow **the same lifecycle rules** as ecosystem repos. Partner source registry in `sources.md` links `source_id` → `repo_id` list.

Partner blog announcement + GitHub release of same version → **cluster** into one canonical signal (prefer blog for narrative, attach GitHub for technical detail).

---

## Curated Watchlist Governance

### Adding a Repository

1. Business justification (client project, practice standard, partner dependency)
2. Assign tier, domains, semver policy
3. 14-day ingest-only pilot (ledger populated, no feed surfacing)
4. Practice lead approval
5. Enable surfacing

### Removing a Repository

- Set `enabled = false`; retain ledger history
- Do not delete historical signals

### Quarterly Review

- Remove repos with no releases in 18 months (archive tier)
- Upgrade/downgrade tier based on project usage

---

## Storage Schema (Conceptual)

### `repository_registry`

Registry records as defined above.

### `repository_version_ledger`

| Column | Type |
|--------|------|
| `repo_id` | string PK part |
| `version` | string PK part |
| `signal_id` | FK |
| `surfaced_at` | timestamp |
| `semver_major` | int |
| `semver_minor` | int |
| `semver_patch` | int |

### `repository_poll_state`

| Column | Type |
|--------|------|
| `repo_id` | string PK |
| `last_release_id` | string |
| `last_polled_at` | timestamp |
| `etag` | string |

---

## Noise Controls (OSS-Specific)

| Rule ID | Condition | Action |
|---------|-----------|--------|
| `OSS-001` | Version in ledger | Suppress |
| `OSS-002` | Patch bump, Tier B/C, no security keyword | Suppress |
| `OSS-003` | Fork or duplicate repo name | Drop |
| `OSS-004` | Release marked `draft` or `prerelease` | Hold (Tier A security excepted) |
| `OSS-005` | >3 OSS signals same domain in 24h | Apply diversity cap in ranking |

---

## MVP Scope

MVP includes:

- [ ] Registry with ≥10 Tier A repos (LangGraph-class + 2 partner org repos)
- [ ] Poll-based ingestion with version ledger
- [ ] No re-surface without version change
- [ ] OSS signals in intelligence store with full enrichment

MVP excludes:

- GitHub webhooks (poll acceptable locally)
- Automatic watchlist discovery
- Dependency graph transitive monitoring

---

## Related Documents

- `sources.md` — Partner GitHub source IDs
- `signal_rules.md` — OSS classification rules
- `scoring_model.md` — Tier-based score modifiers
- `output_schema.md` — `github` object on intelligence records
- `strategic_signal_framework.md` — Lifecycle philosophy
