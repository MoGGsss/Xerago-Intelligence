"""Pydantic models for registry/sources.yaml and registry/repos.yaml."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

DomainSlug = Literal[
    "ai-ml",
    "customer-experience",
    "martech",
    "analytics",
    "personalization",
    "automation",
    "enterprise-ai",
    "open-source-ecosystem",
    "research-signals",
    "industry-trends",
    "cloud-platforms",
    "data-engineering",
]

Priority = Literal["P0", "P1", "P2", "P3", "P4"]
RepoPriority = Literal["P0", "P1", "P2"]
EntityGroup = Literal["partner", "ai_vendor", "research", "industry", "ecosystem"]
TrustTier = Literal["T1", "T2", "T3"]
SourceType = Literal[
    "blog",
    "docs",
    "github",
    "rss",
    "api",
    "newsletter",
    "press",
    "changelog",
    "community",
    "sitemap",
]
IngestionMethod = Literal[
    "pull_rss",
    "pull_api",
    "github_releases",
    "github_org_releases",
    "sitemap",
    "scrape",
    "email_parse",
    "manual",
    "webhook",
]
SemverAction = Literal["promote", "promote_if_keywords", "hold"]
RepoTier = Literal["A", "B", "C"]


class RegistryMetadata(BaseModel):
    updated_at: str
    description: str
    documentation: str | None = None


class EntityEntry(BaseModel):
    slug: str
    display_name: str
    group: EntityGroup
    priority: Priority
    default_domains: list[DomainSlug] = Field(default_factory=list)
    product_tags: list[str] = Field(default_factory=list)
    notes: str | None = None


class SourceFilters(BaseModel):
    tags: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)


class SourceEntry(BaseModel):
    source_id: str
    name: str
    entity: str
    source_type: SourceType
    ingestion_method: IngestionMethod
    trust_tier: TrustTier
    priority: Priority
    enabled: bool
    base_url: str | None = None
    feed_url: str | None = None
    refresh_cadence: str | None = None
    default_domains: list[DomainSlug] = Field(default_factory=list)
    rate_limit_rpm: int | None = None
    github_org: str | None = None
    filters: SourceFilters | None = None
    mvp_wave: int | None = Field(default=None, ge=1, le=3)
    notes: str | None = None


class SourcesRegistry(BaseModel):
    version: str
    schema_path: str | None = Field(default=None, alias="schema")
    metadata: RegistryMetadata | None = None
    entities: list[EntityEntry] = Field(default_factory=list)
    sources: list[SourceEntry]
    taxonomy: dict[str, Any] | None = None

    @model_validator(mode="after")
    def validate_referential_integrity(self) -> SourcesRegistry:
        entity_slugs = {entity.slug for entity in self.entities}
        if self.entities:
            _assert_unique([entity.slug for entity in self.entities], "entity slug")
        _assert_unique([source.source_id for source in self.sources], "source_id")
        unknown = {source.entity for source in self.sources} - entity_slugs
        if self.entities and unknown:
            raise ValueError(
                f"Sources reference unknown entities: {sorted(unknown)}"
            )
        return self


class SemverPolicy(BaseModel):
    major: SemverAction
    minor: SemverAction
    patch: SemverAction
    non_semver: SemverAction | None = None
    patch_keywords: list[str] = Field(default_factory=list)
    minor_keywords: list[str] = Field(default_factory=list)
    milestone_keywords: list[str] = Field(default_factory=list)


class TierDefinition(BaseModel):
    priority: RepoPriority
    poll_cadence: str
    description: str
    semver_policy: SemverPolicy


class RepositoryEntry(BaseModel):
    repo_id: str
    display_name: str
    tier: RepoTier
    entity: str
    domains: list[DomainSlug]
    track_releases: bool
    semver_policy: SemverPolicy
    enabled: bool
    primary_domain: DomainSlug | None = None
    track_tags: bool = False
    milestone_keywords: list[str] = Field(default_factory=list)
    priority: RepoPriority | None = None
    poll_cadence: str | None = None
    related_source_id: str | None = None
    product_tags: list[str] = Field(default_factory=list)
    mvp: bool = False
    notes: str | None = None

    @field_validator("repo_id")
    @classmethod
    def normalize_repo_id(cls, value: str) -> str:
        return value.strip().lower()


class ReposRegistry(BaseModel):
    version: str
    schema_path: str | None = Field(default=None, alias="schema")
    metadata: RegistryMetadata | None = None
    tier_definitions: dict[RepoTier, TierDefinition] = Field(default_factory=dict)
    repositories: list[RepositoryEntry]

    @model_validator(mode="after")
    def validate_repositories(self) -> ReposRegistry:
        _assert_unique([repo.repo_id for repo in self.repositories], "repo_id")
        return self


class RegistryBundle(BaseModel):
    """Loaded sources and repos registries."""

    project_root: str
    sources: SourcesRegistry
    repos: ReposRegistry

    @property
    def enabled_source_count(self) -> int:
        return sum(1 for source in self.sources.sources if source.enabled)

    @property
    def enabled_repo_count(self) -> int:
        return sum(1 for repo in self.repos.repositories if repo.enabled)

    @property
    def mvp_repo_count(self) -> int:
        return sum(1 for repo in self.repos.repositories if repo.mvp and repo.enabled)


def _assert_unique(values: list[str], label: str) -> None:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen:
            duplicates.append(value)
        seen.add(value)
    if duplicates:
        raise ValueError(f"Duplicate {label}(s): {sorted(set(duplicates))}")
