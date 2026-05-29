"""MySQL connectivity via SQLAlchemy + PyMySQL."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Engine, create_engine as sa_create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from xerago_intelligence.config import get_settings

_engine: Engine | None = None


@dataclass(frozen=True)
class ConnectionInfo:
    ok: bool
    mysql_version: str | None = None
    current_database: str | None = None
    error: str | None = None


def create_engine(*, echo: bool | None = None) -> Engine:
    """Create a new SQLAlchemy engine (does not use the process singleton)."""
    settings = get_settings()
    return sa_create_engine(
        settings.resolved_database_url(),
        echo=settings.db_echo if echo is None else echo,
        pool_pre_ping=True,
        pool_recycle=3600,
        connect_args={"charset": settings.mysql_charset},
    )


def get_engine() -> Engine:
    """Return a shared engine instance for this process."""
    global _engine
    if _engine is None:
        _engine = create_engine()
    return _engine


def dispose_engine() -> None:
    """Dispose the shared engine and release pool connections."""
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None


def check_connection() -> bool:
    """Return True if MySQL accepts a connection and responds to SELECT 1."""
    return probe_connection().ok


def probe_connection() -> ConnectionInfo:
    """Run a connectivity probe and return structured results."""
    try:
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
            version = connection.execute(text("SELECT VERSION()")).scalar_one()
            database = connection.execute(text("SELECT DATABASE()")).scalar_one()
        return ConnectionInfo(
            ok=True,
            mysql_version=str(version),
            current_database=str(database) if database is not None else None,
        )
    except SQLAlchemyError as exc:
        return ConnectionInfo(ok=False, error=str(exc))
