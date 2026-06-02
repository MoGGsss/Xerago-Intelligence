"""RSS and feed ingestion (import submodules directly to avoid import cycles)."""

from xerago_intelligence.ingest.feed_fetch import FeedFetchConfig, FeedFetchError

__all__ = [
    "FeedFetchConfig",
    "FeedFetchError",
]
