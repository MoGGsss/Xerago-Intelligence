"""URL normalization helpers."""

from __future__ import annotations

from urllib.parse import urldefrag, urlparse, urlunparse


def normalize_url(url: str) -> str:
    """Normalize URL for duplicate detection (strip fragment, trim, lowercase host)."""
    url = url.strip()
    url, _fragment = urldefrag(url)
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    scheme = parsed.scheme.lower() or "https"
    path = parsed.path or ""
    normalized = urlunparse((scheme, netloc, path, parsed.params, parsed.query, ""))
    return normalized.rstrip("/") if path == "/" else normalized
