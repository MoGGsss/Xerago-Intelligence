"""RSS feed ingestion using requests + feedparser (no FreshRSS)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from time import struct_time

import requests
from sqlalchemy.orm import Session

from xerago_intelligence.db.repositories.artifact_repository import ArtifactRepository
from xerago_intelligence.db.repositories.cursor_repository import CursorRepository
from xerago_intelligence.ingest.cursor_state import compute_watermark, is_newer_than_cursor
from xerago_intelligence.ingest.diagnostics import emit, timed_step
from xerago_intelligence.ingest.feed_fetch import (
    FeedFetchConfig,
    FeedFetchError,
    create_http_session,
    fetch_and_parse_feed,
)
from xerago_intelligence.utils.url import normalize_url

logger = logging.getLogger(__name__)

OPENAI_NEWS_RSS = "https://openai.com/news/rss.xml"
DEFAULT_TEST_SOURCE_ID = "openai-blog"


@dataclass(frozen=True)
class RssIngestResult:
    feed_url: str
    source_id: str
    fetched: int
    processed: int
    inserted: int
    skipped: int
    skipped_cursor: int = 0
    skipped_duplicate: int = 0
    skipped_invalid: int = 0
    http_status: int | None = None
    content_length: int | None = None

    # Sprint 2A compatibility
    @property
    def fetched_entries(self) -> int:
        return self.fetched

    @property
    def skipped_duplicates(self) -> int:
        return self.skipped_duplicate

    @property
    def inserts_attempted(self) -> int:
        return self.processed

    @property
    def inserts_committed(self) -> int:
        return self.inserted


class RssIngestionService:
    """Fetch an RSS/Atom feed and persist new entries as artifacts."""

    def __init__(
        self,
        session: Session,
        *,
        http_session: requests.Session | None = None,
        fetch_config: FeedFetchConfig | None = None,
    ) -> None:
        self._session = session
        self._repo = ArtifactRepository(session)
        self._cursor_repo = CursorRepository(session)
        self._fetch_config = fetch_config or FeedFetchConfig()
        self._http_session = http_session
        self._owns_http_session = http_session is None

    def close(self) -> None:
        if self._owns_http_session and self._http_session is not None:
            self._http_session.close()
            self._http_session = None

    def ingest_feed(self, feed_url: str, source_id: str) -> RssIngestResult:
        logger.info("Fetching RSS feed: %s (source_id=%s)", feed_url, source_id)
        emit(f"[diag] RSS ingest start — source_id={source_id}")

        cursor_before = self._cursor_repo.get_state(source_id)
        if cursor_before and cursor_before.last_published_at:
            emit(
                f"[diag] Cursor before ingest: "
                f"last_published_at={cursor_before.last_published_at.isoformat()}"
            )
        else:
            emit("[diag] Cursor before ingest: (none — full feed scan)")

        http = self._http_session
        if http is None:
            with timed_step("Create HTTP session"):
                http = create_http_session(self._fetch_config)
            if self._owns_http_session:
                self._http_session = http

        try:
            document = fetch_and_parse_feed(
                feed_url,
                session=http,
                config=self._fetch_config,
            )
        except FeedFetchError:
            raise

        parsed = document.parsed
        fetched = len(parsed.entries)
        processed = 0
        inserted = 0
        skipped_cursor = 0
        skipped_duplicate = 0
        skipped_invalid = 0
        observed_for_watermark: list[tuple[datetime, str | None]] = []

        emit(f"[diag] Persisting entries — fetched={fetched}")
        with timed_step("Persist artifacts (incremental)"):
            for entry in parsed.entries:
                record = _entry_to_fields(entry)
                if record is None:
                    skipped_invalid += 1
                    continue

                title, url, published_at, raw_content = record
                entry_id = _entry_id(entry)
                observed_for_watermark.append((published_at, entry_id))

                if not is_newer_than_cursor(
                    published_at=published_at,
                    entry_id=entry_id,
                    cursor=cursor_before,
                ):
                    skipped_cursor += 1
                    continue

                processed += 1
                _artifact, created = self._repo.insert_article(
                    source_id=source_id,
                    title=title,
                    url=url,
                    published_at=published_at,
                    raw_content=raw_content,
                )
                if created:
                    inserted += 1
                    logger.debug("Inserted artifact: %s", url)
                else:
                    skipped_duplicate += 1

        skipped = skipped_cursor + skipped_duplicate + skipped_invalid

        new_watermark = compute_watermark(observed_for_watermark)
        if new_watermark is not None:
            with timed_step("Update ingest cursor"):
                self._cursor_repo.save_state(source_id, new_watermark)
            emit(
                f"[diag] Cursor updated: "
                f"last_published_at={new_watermark.last_published_at.isoformat()}"
            )

        emit(
            f"[diag] Metrics — fetched={fetched} processed={processed} "
            f"inserted={inserted} skipped={skipped} "
            f"(cursor={skipped_cursor} dup={skipped_duplicate} invalid={skipped_invalid})"
        )

        logger.info(
            "Ingest complete for %s: fetched=%s processed=%s inserted=%s skipped=%s",
            feed_url,
            fetched,
            processed,
            inserted,
            skipped,
        )

        return RssIngestResult(
            feed_url=feed_url,
            source_id=source_id,
            fetched=fetched,
            processed=processed,
            inserted=inserted,
            skipped=skipped,
            skipped_cursor=skipped_cursor,
            skipped_duplicate=skipped_duplicate,
            skipped_invalid=skipped_invalid,
            http_status=document.http_status,
            content_length=document.content_length,
        )


def _entry_id(entry: object) -> str | None:
    for attr in ("id", "guid", "link"):
        value = getattr(entry, attr, None)
        if value:
            return str(value).strip()
    return None


def _entry_to_fields(
    entry: object,
) -> tuple[str, str, datetime, str | None] | None:
    """Map a feedparser entry to artifact fields."""
    title = _coalesce(getattr(entry, "title", None))
    link = _coalesce(getattr(entry, "link", None))
    if not title or not link:
        return None

    published_at = _parse_published(entry)
    raw_content = _extract_raw_content(entry)
    return title, normalize_url(link), published_at, raw_content


def _coalesce(value: object | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _parse_published(entry: object) -> datetime:
    for attr in ("published_parsed", "updated_parsed", "created_parsed"):
        parsed = getattr(entry, attr, None)
        if parsed is not None:
            return _struct_time_to_utc(parsed)
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _struct_time_to_utc(st: struct_time) -> datetime:
    return datetime(
        st.tm_year,
        st.tm_mon,
        st.tm_mday,
        st.tm_hour,
        st.tm_min,
        st.tm_sec,
        tzinfo=timezone.utc,
    ).replace(tzinfo=None)


def _extract_raw_content(entry: object) -> str | None:
    parts: list[str] = []
    summary = _coalesce(getattr(entry, "summary", None))
    if summary:
        parts.append(summary)
    content_list = getattr(entry, "content", None) or []
    for item in content_list:
        value = _coalesce(getattr(item, "value", None))
        if value and value not in parts:
            parts.append(value)
    description = _coalesce(getattr(entry, "description", None))
    if description and description not in parts:
        parts.append(description)
    if not parts:
        return None
    return "\n\n".join(parts)
