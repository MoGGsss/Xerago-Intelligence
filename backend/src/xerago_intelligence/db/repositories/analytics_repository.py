"""Read-only analytics aggregations over existing intelligence tables."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from xerago_intelligence.db.models.article_feedback import ArticleFeedback
from xerago_intelligence.db.models.artifact import Artifact
from xerago_intelligence.db.models.artifact_department_mapping import ArtifactDepartmentMapping
from xerago_intelligence.db.models.artifact_enrichment import ArtifactEnrichment
from xerago_intelligence.db.models.intelligence_run import IntelligenceRun
from xerago_intelligence.db.models.rss_source import RssSource


@dataclass(frozen=True)
class RankedCount:
    label: str
    count: int
    avg_score: float | None = None


@dataclass(frozen=True)
class UsefulArticleRow:
    artifact_id: str
    title: str
    positive_count: int
    strategic_score: int | None
    url: str


class AnalyticsRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _start_of_today(self) -> datetime:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        return now.replace(hour=0, minute=0, second=0, microsecond=0)

    def count_articles_today(self) -> int:
        return int(
            self._session.scalar(
                select(func.count())
                .select_from(Artifact)
                .where(Artifact.ingested_at >= self._start_of_today())
            )
            or 0
        )

    def count_active_sources(self) -> int:
        return int(
            self._session.scalar(
                select(func.count())
                .select_from(RssSource)
                .where(RssSource.active_flag.is_(True))
            )
            or 0
        )

    def count_enriched_articles(self) -> int:
        return int(
            self._session.scalar(select(func.count()).select_from(ArtifactEnrichment)) or 0
        )

    def feedback_totals(self) -> tuple[int, int, int]:
        positive = int(
            self._session.scalar(
                select(func.count())
                .select_from(ArticleFeedback)
                .where(ArticleFeedback.feedback_type == "positive")
            )
            or 0
        )
        negative = int(
            self._session.scalar(
                select(func.count())
                .select_from(ArticleFeedback)
                .where(ArticleFeedback.feedback_type == "negative")
            )
            or 0
        )
        return positive + negative, positive, negative

    def average_strategic_score(self) -> float | None:
        value = self._session.scalar(
            select(func.avg(ArtifactEnrichment.strategic_score)).where(
                ArtifactEnrichment.strategic_score.is_not(None)
            )
        )
        return round(float(value), 1) if value is not None else None

    def top_departments_by_opportunity(
        self,
        *,
        limit: int = 10,
    ) -> list[RankedCount]:
        rows = self._session.execute(
            select(
                ArtifactDepartmentMapping.department_name,
                func.count(func.distinct(ArtifactDepartmentMapping.artifact_id)),
                func.avg(ArtifactDepartmentMapping.department_opportunity_score),
            )
            .where(ArtifactDepartmentMapping.department_opportunity_score.is_not(None))
            .group_by(ArtifactDepartmentMapping.department_name)
            .order_by(func.avg(ArtifactDepartmentMapping.department_opportunity_score).desc())
            .limit(limit)
        ).all()
        return [
            RankedCount(
                label=str(name),
                count=int(count),
                avg_score=round(float(avg), 1) if avg is not None else None,
            )
            for name, count, avg in rows
        ]

    def department_engagement(self, *, limit: int = 12) -> list[dict[str, int | str]]:
        mapping_counts = dict(
            self._session.execute(
                select(
                    ArtifactDepartmentMapping.department_name,
                    func.count(func.distinct(ArtifactDepartmentMapping.artifact_id)),
                ).group_by(ArtifactDepartmentMapping.department_name)
            ).all()
        )
        feedback_rows = self._session.execute(
            select(
                ArticleFeedback.department_name,
                ArticleFeedback.feedback_type,
                func.count(),
            ).group_by(ArticleFeedback.department_name, ArticleFeedback.feedback_type)
        ).all()

        engagement: dict[str, dict[str, int | str]] = {}
        for dept, mapped in mapping_counts.items():
            engagement[dept] = {
                "department_name": dept,
                "mapped_articles": int(mapped),
                "feedback_count": 0,
                "positive_count": 0,
                "negative_count": 0,
            }

        for dept, feedback_type, count in feedback_rows:
            bucket = engagement.setdefault(
                dept,
                {
                    "department_name": dept,
                    "mapped_articles": 0,
                    "feedback_count": 0,
                    "positive_count": 0,
                    "negative_count": 0,
                },
            )
            bucket["feedback_count"] = int(bucket["feedback_count"]) + int(count)
            if feedback_type == "positive":
                bucket["positive_count"] = int(count)
            elif feedback_type == "negative":
                bucket["negative_count"] = int(count)

        ranked = sorted(
            engagement.values(),
            key=lambda row: (
                int(row["feedback_count"]),
                int(row["mapped_articles"]),
            ),
            reverse=True,
        )
        return ranked[:limit]

    def top_opportunity_categories(self, *, limit: int = 10) -> list[RankedCount]:
        rows = self._session.execute(
            select(
                ArtifactDepartmentMapping.impact_category,
                func.count(),
                func.avg(ArtifactDepartmentMapping.department_opportunity_score),
            )
            .where(ArtifactDepartmentMapping.impact_category.is_not(None))
            .where(ArtifactDepartmentMapping.impact_category != "")
            .group_by(ArtifactDepartmentMapping.impact_category)
            .order_by(func.count().desc())
            .limit(limit)
        ).all()
        return [
            RankedCount(
                label=str(category),
                count=int(count),
                avg_score=round(float(avg), 1) if avg is not None else None,
            )
            for category, count, avg in rows
        ]

    def top_opportunity_types(self, *, limit: int = 10) -> list[RankedCount]:
        rows = self._session.execute(
            select(
                ArtifactDepartmentMapping.opportunity_type,
                func.count(),
                func.avg(ArtifactDepartmentMapping.department_opportunity_score),
            )
            .where(ArtifactDepartmentMapping.opportunity_type.is_not(None))
            .where(ArtifactDepartmentMapping.opportunity_type != "")
            .group_by(ArtifactDepartmentMapping.opportunity_type)
            .order_by(func.count().desc())
            .limit(limit)
        ).all()
        return [
            RankedCount(
                label=str(opportunity_type),
                count=int(count),
                avg_score=round(float(avg), 1) if avg is not None else None,
            )
            for opportunity_type, count, avg in rows
        ]

    def source_contribution(self, *, limit: int = 20) -> list[dict[str, object]]:
        rows = self._session.execute(
            select(
                Artifact.source_id,
                func.count(func.distinct(Artifact.artifact_id)),
                func.count(func.distinct(ArtifactEnrichment.artifact_id)),
                func.avg(ArtifactEnrichment.strategic_score),
            )
            .select_from(Artifact)
            .outerjoin(
                ArtifactEnrichment,
                Artifact.artifact_id == ArtifactEnrichment.artifact_id,
            )
            .group_by(Artifact.source_id)
            .order_by(func.count(func.distinct(Artifact.artifact_id)).desc())
            .limit(limit)
        ).all()

        source_meta = {
            row.source_id: row
            for row in self._session.scalars(select(RssSource)).all()
        }

        result: list[dict[str, object]] = []
        for source_id, article_count, enriched_count, avg_score in rows:
            meta = source_meta.get(source_id)
            result.append(
                {
                    "source_id": source_id,
                    "source_name": meta.source_name if meta else source_id,
                    "source_tier": int(meta.source_tier) if meta else None,
                    "active_flag": bool(meta.active_flag) if meta else None,
                    "article_count": int(article_count),
                    "enriched_count": int(enriched_count or 0),
                    "avg_strategic_score": (
                        round(float(avg_score), 1) if avg_score is not None else None
                    ),
                }
            )
        return result

    def most_useful_articles(self, *, limit: int = 10) -> list[UsefulArticleRow]:
        positive_counts = (
            select(
                ArticleFeedback.artifact_id,
                func.count().label("positive_count"),
            )
            .where(ArticleFeedback.feedback_type == "positive")
            .group_by(ArticleFeedback.artifact_id)
            .subquery()
        )
        rows = self._session.execute(
            select(
                Artifact.artifact_id,
                Artifact.title,
                Artifact.url,
                positive_counts.c.positive_count,
                ArtifactEnrichment.strategic_score,
            )
            .join(positive_counts, Artifact.artifact_id == positive_counts.c.artifact_id)
            .outerjoin(
                ArtifactEnrichment,
                Artifact.artifact_id == ArtifactEnrichment.artifact_id,
            )
            .order_by(positive_counts.c.positive_count.desc())
            .limit(limit)
        ).all()
        return [
            UsefulArticleRow(
                artifact_id=str(artifact_id),
                title=str(title),
                positive_count=int(positive_count),
                strategic_score=int(strategic_score) if strategic_score is not None else None,
                url=str(url),
            )
            for artifact_id, title, url, positive_count, strategic_score in rows
        ]

    def feedback_trends(self, *, days: int = 14) -> list[dict[str, int | str]]:
        since = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days - 1)
        since = since.replace(hour=0, minute=0, second=0, microsecond=0)
        rows = self._session.execute(
            select(
                func.date(ArticleFeedback.created_at),
                ArticleFeedback.feedback_type,
                func.count(),
            )
            .where(ArticleFeedback.created_at >= since)
            .group_by(func.date(ArticleFeedback.created_at), ArticleFeedback.feedback_type)
            .order_by(func.date(ArticleFeedback.created_at))
        ).all()

        by_day: dict[str, dict[str, int | str]] = {}
        for day_value, feedback_type, count in rows:
            day_key = str(day_value)
            bucket = by_day.setdefault(
                day_key,
                {"date": day_key, "positive": 0, "negative": 0, "total": 0},
            )
            if feedback_type == "positive":
                bucket["positive"] = int(count)
            elif feedback_type == "negative":
                bucket["negative"] = int(count)
            bucket["total"] = int(bucket["positive"]) + int(bucket["negative"])

        return [by_day[key] for key in sorted(by_day.keys())]

    def latest_intelligence_run(self) -> IntelligenceRun | None:
        return self._session.scalar(
            select(IntelligenceRun)
            .order_by(IntelligenceRun.started_at.desc())
            .limit(1)
        )
