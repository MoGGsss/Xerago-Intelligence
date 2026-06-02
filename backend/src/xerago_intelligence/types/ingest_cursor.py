"""Ingest cursor value object (DB + ingestion layers)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class IngestCursorState:
    """Per-source incremental ingest watermark."""

    last_published_at: datetime | None = None
    last_entry_id: str | None = None

    def to_json(self) -> str:
        payload = {
            "last_published_at": (
                self.last_published_at.isoformat() if self.last_published_at else None
            ),
            "last_entry_id": self.last_entry_id,
        }
        return json.dumps(payload, separators=(",", ":"))

    @classmethod
    def from_json(cls, raw: str) -> IngestCursorState:
        data = json.loads(raw)
        published_raw = data.get("last_published_at")
        published_at = (
            datetime.fromisoformat(published_raw) if published_raw else None
        )
        return cls(
            last_published_at=published_at,
            last_entry_id=data.get("last_entry_id"),
        )
