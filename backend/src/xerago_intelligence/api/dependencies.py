"""FastAPI dependencies."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session

from xerago_intelligence.db.session import get_session_factory


def get_db() -> Generator[Session, None, None]:
    """Yield a read-only database session per request."""
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()
