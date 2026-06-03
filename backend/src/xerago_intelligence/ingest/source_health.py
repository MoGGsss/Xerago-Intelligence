"""Source health monitoring around RSS ingest cycles."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from xerago_intelligence.db.repositories.rss_source_repository import RssSourceRepository
from xerago_intelligence.ingest.feed_fetch import FeedFetchError
from xerago_intelligence.ingest.rss import RssIngestResult, RssIngestionService

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SourceIngestOutcome:
    source_id: str
    feed_url: str
    status: str
    result: RssIngestResult | None = None
    error_message: str | None = None


class SourceHealthMonitor:
    """Wraps RSS ingest with per-source run logging."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._sources = RssSourceRepository(session)

    def ingest_source(self, source_id: str, feed_url: str) -> SourceIngestOutcome:
        started_at = datetime.now(timezone.utc).replace(tzinfo=None)
        run_id = self._sources.record_run_start(source_id)
        ingestion = RssIngestionService(self._session)
        try:
            result = ingestion.ingest_feed(feed_url, source_id)
        except FeedFetchError as exc:
            self._sources.record_run_failure(
                run_id=run_id,
                source_id=source_id,
                started_at=started_at,
                error_message=str(exc),
            )
            logger.warning("Feed fetch failed for %s: %s", source_id, exc)
            return SourceIngestOutcome(
                source_id=source_id,
                feed_url=feed_url,
                status="failure",
                error_message=str(exc),
            )
        except Exception as exc:
            self._sources.record_run_failure(
                run_id=run_id,
                source_id=source_id,
                started_at=started_at,
                error_message=str(exc),
            )
            raise
        finally:
            ingestion.close()

        self._sources.record_run_success(
            run_id=run_id,
            source_id=source_id,
            started_at=started_at,
            http_status=result.http_status,
            entries_fetched=result.fetched,
            entries_inserted=result.inserted,
            entries_skipped_dup=result.skipped_duplicate,
            entries_skipped_cursor=result.skipped_cursor,
        )
        return SourceIngestOutcome(
            source_id=source_id,
            feed_url=feed_url,
            status="success",
            result=result,
        )
