"""Pydantic models for executive analytics API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class RankedMetricItem(BaseModel):
    label: str
    count: int
    avg_score: float | None = None


class UsefulArticleItem(BaseModel):
    artifact_id: str
    title: str
    url: str
    positive_count: int
    strategic_score: int | None = None


class DepartmentEngagementItem(BaseModel):
    department_name: str
    mapped_articles: int
    feedback_count: int
    positive_count: int
    negative_count: int


class SourceContributionItem(BaseModel):
    source_id: str
    source_name: str
    source_tier: int | None = None
    active_flag: bool | None = None
    article_count: int
    enriched_count: int
    avg_strategic_score: float | None = None


class FeedbackTrendPoint(BaseModel):
    date: str
    positive: int
    negative: int
    total: int


class FeedbackSummary(BaseModel):
    total: int
    positive: int
    negative: int
    positive_pct: float = Field(ge=0, le=100)
    trends: list[FeedbackTrendPoint]


class AnalyticsOverviewResponse(BaseModel):
    articles_today: int
    active_sources: int
    enriched_articles: int
    average_strategic_score: float | None = None
    feedback_total: int
    feedback_positive: int
    feedback_negative: int
    last_refresh_at: datetime | None = None
    last_refresh_status: str | None = None


class AnalyticsDepartmentsResponse(BaseModel):
    top_departments: list[RankedMetricItem]
    department_engagement: list[DepartmentEngagementItem]


class AnalyticsOpportunitiesResponse(BaseModel):
    top_opportunity_categories: list[RankedMetricItem]
    top_opportunity_types: list[RankedMetricItem]


class AnalyticsSourcesResponse(BaseModel):
    source_contribution: list[SourceContributionItem]


class AnalyticsFeedbackResponse(BaseModel):
    positive_vs_negative: FeedbackSummary
    most_useful_articles: list[UsefulArticleItem]
