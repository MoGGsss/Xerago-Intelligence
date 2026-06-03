"""System monitoring API."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from xerago_intelligence.api.dependencies import get_db
from xerago_intelligence.api.schemas.system import SystemStatusResponse
from xerago_intelligence.api.services.system_status import build_system_status

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/status", response_model=SystemStatusResponse)
def system_status(db: Session = Depends(get_db)) -> SystemStatusResponse:
    return build_system_status(db)
