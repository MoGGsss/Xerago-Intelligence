"""HTTP feed fetching with certifi SSL verification and retry-ready session."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import certifi
import feedparser
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from xerago_intelligence.ingest.diagnostics import emit, timed_step

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_FACTOR = 0.5
DEFAULT_RETRY_STATUS_CODES = (429, 500, 502, 503, 504)


class FeedFetchError(Exception):
    """Raised when a feed cannot be fetched or parsed."""


@dataclass(frozen=True)
class FeedFetchConfig:
    """HTTP fetch settings (retry-ready via urllib3 Retry on the session adapter)."""

    timeout: float = DEFAULT_TIMEOUT_SECONDS
    max_retries: int = DEFAULT_MAX_RETRIES
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR
    retry_status_codes: tuple[int, ...] = DEFAULT_RETRY_STATUS_CODES
    user_agent: str = (
        "XeragoIntelligenceEngine/0.5 (+https://xerago.com; RSS ingest)"
    )


@dataclass
class FeedDocument:
    """Fetched and parsed RSS/Atom document."""

    feed_url: str
    parsed: Any
    http_status: int
    content_length: int


def create_http_session(config: FeedFetchConfig) -> requests.Session:
    """
    Build a requests session with certifi CA bundle and retry-enabled adapters.

    SSL verification is always enabled; never disable certificate checks.
    """
    session = requests.Session()
    session.verify = certifi.where()
    session.headers.update(
        {
            "User-Agent": config.user_agent,
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
        }
    )

    retry_strategy = Retry(
        total=config.max_retries,
        connect=config.max_retries,
        read=config.max_retries,
        backoff_factor=config.backoff_factor,
        status_forcelist=list(config.retry_status_codes),
        allowed_methods=frozenset({"GET", "HEAD"}),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def fetch_feed_bytes(
    feed_url: str,
    *,
    session: requests.Session | None = None,
    config: FeedFetchConfig | None = None,
) -> tuple[bytes, int]:
    """
    Download feed body over HTTPS with SSL verification.

    Returns (content, http_status_code).
    """
    config = config or FeedFetchConfig()
    owns_session = session is None
    http = session or create_http_session(config)

    try:
        emit(f"[diag] HTTP request start — GET {feed_url}")
        emit(f"[diag] HTTP timeout={config.timeout}s verify=certifi")
        with timed_step("HTTP request"):
            response = http.get(feed_url, timeout=config.timeout)
            status = response.status_code
            content_length = len(response.content)
            emit(f"[diag] HTTP status code: {status}")
            emit(f"[diag] Content length: {content_length} bytes")
            response.raise_for_status()
        return response.content, status
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "?"
        emit(f"[diag] HTTP error: status={status}")
        raise FeedFetchError(
            f"HTTP {status} while fetching feed: {feed_url}"
        ) from exc
    except requests.SSLError as exc:
        emit("[diag] SSL verification failed")
        raise FeedFetchError(
            f"SSL verification failed for feed: {feed_url}. "
            "Ensure certifi is installed and system time is correct."
        ) from exc
    except requests.Timeout as exc:
        emit(f"[diag] HTTP timeout after {config.timeout}s")
        raise FeedFetchError(
            f"Timeout after {config.timeout}s fetching feed: {feed_url}"
        ) from exc
    except requests.RequestException as exc:
        emit(f"[diag] HTTP request failed: {exc}")
        raise FeedFetchError(f"Request failed for feed: {feed_url}") from exc
    finally:
        if owns_session:
            http.close()


def parse_feed_content(
    content: bytes,
    *,
    feed_url: str,
) -> Any:
    """Parse raw feed bytes with feedparser (no network I/O)."""
    with timed_step("Feed parse (feedparser)"):
        parsed = feedparser.parse(content)
    if parsed.bozo and not parsed.entries:
        detail = parsed.bozo_exception
        emit(f"[diag] Feed parse failed: {detail}")
        raise FeedFetchError(
            f"Failed to parse RSS/Atom content from {feed_url}: {detail}"
        )
    if parsed.bozo:
        logger.warning(
            "Feed parsed with warnings for %s: %s",
            feed_url,
            parsed.bozo_exception,
        )
        emit(f"[diag] Feed parsed with warnings: {parsed.bozo_exception}")
    else:
        emit("[diag] Feed parsed: OK")
    entry_count = len(parsed.entries)
    emit(f"[diag] Number of entries found: {entry_count}")
    return parsed


def fetch_and_parse_feed(
    feed_url: str,
    *,
    session: requests.Session | None = None,
    config: FeedFetchConfig | None = None,
) -> FeedDocument:
    """
    Fetch feed via requests (certifi SSL) and parse with feedparser.

    1. requests.get(feed_url, timeout=...)
    2. response.raise_for_status()
    3. feedparser.parse(response.content)
    """
    content, status = fetch_feed_bytes(feed_url, session=session, config=config)
    parsed = parse_feed_content(content, feed_url=feed_url)
    return FeedDocument(
        feed_url=feed_url,
        parsed=parsed,
        http_status=status,
        content_length=len(content),
    )
