"""Incremental ingest filtering (ingestion layer only)."""

from __future__ import annotations

from datetime import datetime

from xerago_intelligence.types.ingest_cursor import IngestCursorState


def is_newer_than_cursor(
    *,
    published_at: datetime,
    entry_id: str | None,
    cursor: IngestCursorState | None,
) -> bool:
    """
    Return True if the entry should be processed (not yet covered by cursor).

    Entries at or before the cursor watermark are skipped on subsequent runs.
    ``entry_id`` is accepted for API symmetry and future extensions.
    """
    _ = entry_id
    if cursor is None or cursor.last_published_at is None:
        return True
    return published_at > cursor.last_published_at


def compute_watermark(
    entries: list[tuple[datetime, str | None]],
) -> IngestCursorState | None:
    """Derive the next cursor from observed feed entries (max published_at)."""
    if not entries:
        return None
    max_published = max(published for published, _ in entries)
    candidates = [
        (entry_id, published)
        for published, entry_id in entries
        if published == max_published
    ]
    last_entry_id = candidates[0][0] if candidates else None
    return IngestCursorState(
        last_published_at=max_published,
        last_entry_id=last_entry_id,
    )
