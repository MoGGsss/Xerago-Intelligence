"""Persistence layer for ingest_cursors."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from xerago_intelligence.db.models.ingest_cursor import IngestCursor
from xerago_intelligence.types.ingest_cursor import IngestCursorState


class CursorRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_state(self, source_id: str) -> IngestCursorState | None:
        row = self._session.get(IngestCursor, source_id)
        if row is None:
            return None
        if row.last_published_at is not None:
            return IngestCursorState(
                last_published_at=row.last_published_at,
                last_entry_id=row.last_entry_id,
            )
        try:
            return IngestCursorState.from_json(row.cursor_value)
        except (ValueError, TypeError):
            return IngestCursorState(
                last_published_at=None,
                last_entry_id=row.last_entry_id,
            )

    def get_row(self, source_id: str) -> IngestCursor | None:
        return self._session.get(IngestCursor, source_id)

    def save_state(self, source_id: str, state: IngestCursorState) -> IngestCursor:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        row = self._session.get(IngestCursor, source_id)
        if row is None:
            row = IngestCursor(
                source_id=source_id,
                cursor_value=state.to_json(),
                last_entry_id=state.last_entry_id,
                last_published_at=state.last_published_at,
                updated_at=now,
            )
            self._session.add(row)
        else:
            row.cursor_value = state.to_json()
            row.last_entry_id = state.last_entry_id
            row.last_published_at = state.last_published_at
            row.updated_at = now
        self._session.flush()
        return row

    def list_all(self) -> list[IngestCursor]:
        return list(self._session.scalars(select(IngestCursor)).all())
