"""FastAPI read-only intelligence API."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from xerago_intelligence.api.dependencies import get_db
from xerago_intelligence.api.routers import (
    analytics,
    feedback,
    intelligence,
    prototype,
    sources,
    system,
)
from xerago_intelligence.api.schemas.intelligence import HealthResponse
from xerago_intelligence.config import get_settings
from xerago_intelligence.db.connection import probe_connection
from xerago_intelligence.ingest.scheduler import IngestionScheduler

logger = logging.getLogger(__name__)

_scheduler: IngestionScheduler | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    del app
    global _scheduler
    settings = get_settings()
    interval_seconds = settings.ingest_scheduler_interval_minutes * 60
    _scheduler = IngestionScheduler(interval_seconds=interval_seconds)
    _scheduler.start()
    logger.info(
        "API startup: intelligence refresh scheduler started "
        "(interval=%ss thread=intelligence-refresh-scheduler)",
        interval_seconds,
    )
    try:
        yield
    finally:
        if _scheduler is not None:
            _scheduler.stop()
            _scheduler = None

app = FastAPI(
    title="Xerago Intelligence Engine API",
    description="Read-only intelligence feed (MVP)",
    version="0.5.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(intelligence.router, prefix="/v1")
app.include_router(feedback.router, prefix="/v1")
app.include_router(sources.router, prefix="/v1")
app.include_router(system.router, prefix="/v1")
app.include_router(analytics.router, prefix="/v1")
app.include_router(prototype.router, prefix="/v1")


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health(db: Session = Depends(get_db)) -> HealthResponse:
    _ = db  # ensure session factory initializes
    db_status = "ok" if probe_connection().ok else "error"
    return HealthResponse(status="ok", database=db_status)
