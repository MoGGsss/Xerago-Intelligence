"""Optional diagnostic output for ingest pipelines (observability only)."""

from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import Generator

logger = logging.getLogger(__name__)

_enabled: bool = False


def enable_diagnostics(enabled: bool = True) -> None:
    """Turn on flushed stdout diagnostics (e.g. from verify scripts)."""
    global _enabled
    _enabled = enabled


def is_enabled() -> bool:
    return _enabled


def emit(message: str) -> None:
    """Log and optionally print immediately (unbuffered)."""
    logger.info(message)
    if _enabled:
        print(message, flush=True)


@contextmanager
def timed_step(label: str) -> Generator[None, None, None]:
    """Emit start/done messages with elapsed seconds."""
    emit(f"[diag] {label} — start")
    started = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - started
        emit(f"[diag] {label} — done ({elapsed:.3f}s)")
