"""Executive analytics API (read-only aggregates)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from xerago_intelligence.api.dependencies import get_db
from xerago_intelligence.api.schemas.analytics import (
    AnalyticsDepartmentsResponse,
    AnalyticsFeedbackResponse,
    AnalyticsOpportunitiesResponse,
    AnalyticsOverviewResponse,
    AnalyticsSourcesResponse,
    DepartmentEngagementItem,
    FeedbackSummary,
    FeedbackTrendPoint,
    RankedMetricItem,
    SourceContributionItem,
    UsefulArticleItem,
)
from xerago_intelligence.db.repositories.analytics_repository import AnalyticsRepository

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _ranked(items: list) -> list[RankedMetricItem]:
    return [
        RankedMetricItem(
            label=item.label,
            count=item.count,
            avg_score=item.avg_score,
        )
        for item in items
    ]


@router.get("/overview", response_model=AnalyticsOverviewResponse)
def analytics_overview(db: Session = Depends(get_db)) -> AnalyticsOverviewResponse:
    repo = AnalyticsRepository(db)
    total, positive, negative = repo.feedback_totals()
    latest = repo.latest_intelligence_run()
    return AnalyticsOverviewResponse(
        articles_today=repo.count_articles_today(),
        active_sources=repo.count_active_sources(),
        enriched_articles=repo.count_enriched_articles(),
        average_strategic_score=repo.average_strategic_score(),
        feedback_total=total,
        feedback_positive=positive,
        feedback_negative=negative,
        last_refresh_at=latest.completed_at if latest else None,
        last_refresh_status=latest.status if latest else None,
    )


@router.get("/departments", response_model=AnalyticsDepartmentsResponse)
def analytics_departments(
    limit: int = Query(10, ge=1, le=25),
    db: Session = Depends(get_db),
) -> AnalyticsDepartmentsResponse:
    repo = AnalyticsRepository(db)
    return AnalyticsDepartmentsResponse(
        top_departments=_ranked(repo.top_departments_by_opportunity(limit=limit)),
        department_engagement=[
            DepartmentEngagementItem(
                department_name=str(row["department_name"]),
                mapped_articles=int(row["mapped_articles"]),
                feedback_count=int(row["feedback_count"]),
                positive_count=int(row["positive_count"]),
                negative_count=int(row["negative_count"]),
            )
            for row in repo.department_engagement(limit=limit)
        ],
    )


@router.get("/opportunities", response_model=AnalyticsOpportunitiesResponse)
def analytics_opportunities(
    limit: int = Query(10, ge=1, le=25),
    db: Session = Depends(get_db),
) -> AnalyticsOpportunitiesResponse:
    repo = AnalyticsRepository(db)
    return AnalyticsOpportunitiesResponse(
        top_opportunity_categories=_ranked(repo.top_opportunity_categories(limit=limit)),
        top_opportunity_types=_ranked(repo.top_opportunity_types(limit=limit)),
    )


@router.get("/sources", response_model=AnalyticsSourcesResponse)
def analytics_sources(
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
) -> AnalyticsSourcesResponse:
    repo = AnalyticsRepository(db)
    return AnalyticsSourcesResponse(
        source_contribution=[
            SourceContributionItem(
                source_id=str(row["source_id"]),
                source_name=str(row["source_name"]),
                source_tier=row["source_tier"],  # type: ignore[arg-type]
                active_flag=row["active_flag"],  # type: ignore[arg-type]
                article_count=int(row["article_count"]),
                enriched_count=int(row["enriched_count"]),
                avg_strategic_score=row["avg_strategic_score"],  # type: ignore[arg-type]
            )
            for row in repo.source_contribution(limit=limit)
        ]
    )


@router.get("/feedback", response_model=AnalyticsFeedbackResponse)
def analytics_feedback(
    days: int = Query(14, ge=7, le=90),
    limit: int = Query(10, ge=1, le=25),
    db: Session = Depends(get_db),
) -> AnalyticsFeedbackResponse:
    repo = AnalyticsRepository(db)
    total, positive, negative = repo.feedback_totals()
    positive_pct = round((positive / total) * 100, 1) if total else 0.0
    trends = [
        FeedbackTrendPoint(
            date=str(row["date"]),
            positive=int(row["positive"]),
            negative=int(row["negative"]),
            total=int(row["total"]),
        )
        for row in repo.feedback_trends(days=days)
    ]
    return AnalyticsFeedbackResponse(
        positive_vs_negative=FeedbackSummary(
            total=total,
            positive=positive,
            negative=negative,
            positive_pct=positive_pct,
            trends=trends,
        ),
        most_useful_articles=[
            UsefulArticleItem(
                artifact_id=row.artifact_id,
                title=row.title,
                url=row.url,
                positive_count=row.positive_count,
                strategic_score=row.strategic_score,
            )
            for row in repo.most_useful_articles(limit=limit)
        ],
    )
