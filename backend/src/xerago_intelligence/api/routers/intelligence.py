"""Intelligence read API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from xerago_intelligence.api.dependencies import get_db
from xerago_intelligence.api.schemas.intelligence import (
    IntelligenceItem,
    IntelligenceListResponse,
)
from xerago_intelligence.db.repositories.intelligence_query_repository import (
    IntelligenceListFilters,
    IntelligenceQueryRepository,
)
from xerago_intelligence.types.intelligence import IntelligenceRecord

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


def _to_item(record: IntelligenceRecord) -> IntelligenceItem:
    return IntelligenceItem(
        artifact_id=record.artifact_id,
        title=record.title,
        url=record.url,
        published_at=record.published_at,
        summary=record.summary,
        why_it_matters=record.why_it_matters,
        domain=record.domain,
        signal_type=record.signal_type,
        confidence_score=record.confidence_score,
        validation_status=record.validation_status,
        strategic_score=record.strategic_score,
        priority_level=record.priority_level,
        department=record.department,
    )


@router.get("", response_model=IntelligenceListResponse)
def list_intelligence(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    domain: str | None = Query(None),
    priority: str | None = Query(None),
    q: str | None = Query(None),
    db: Session = Depends(get_db),
) -> IntelligenceListResponse:
    repo = IntelligenceQueryRepository(db)
    result = repo.list_intelligence(
        IntelligenceListFilters(
            page=page,
            page_size=page_size,
            domain=domain,
            priority=priority,
            query=q,
        )
    )
    return IntelligenceListResponse(
        items=[_to_item(item) for item in result.items],
        page=result.page,
        page_size=result.page_size,
        total=result.total,
    )


@router.get("/top", response_model=list[IntelligenceItem])
def list_top_intelligence(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[IntelligenceItem]:
    repo = IntelligenceQueryRepository(db)
    records = repo.list_top(limit=limit)
    return [_to_item(record) for record in records]


@router.get("/domain/{domain}", response_model=IntelligenceListResponse)
def list_intelligence_by_domain(
    domain: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> IntelligenceListResponse:
    repo = IntelligenceQueryRepository(db)
    result = repo.list_intelligence(
        IntelligenceListFilters(
            page=page,
            page_size=page_size,
            domain=domain,
        )
    )
    return IntelligenceListResponse(
        items=[_to_item(item) for item in result.items],
        page=result.page,
        page_size=result.page_size,
        total=result.total,
    )


@router.get("/priority/{priority}", response_model=IntelligenceListResponse)
def list_intelligence_by_priority(
    priority: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> IntelligenceListResponse:
    repo = IntelligenceQueryRepository(db)
    result = repo.list_intelligence(
        IntelligenceListFilters(
            page=page,
            page_size=page_size,
            priority=priority,
        )
    )
    return IntelligenceListResponse(
        items=[_to_item(item) for item in result.items],
        page=result.page,
        page_size=result.page_size,
        total=result.total,
    )


@router.get("/search", response_model=IntelligenceListResponse)
def search_intelligence(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> IntelligenceListResponse:
    repo = IntelligenceQueryRepository(db)
    result = repo.list_intelligence(
        IntelligenceListFilters(
            page=page,
            page_size=page_size,
            query=q,
        )
    )
    return IntelligenceListResponse(
        items=[_to_item(item) for item in result.items],
        page=result.page,
        page_size=result.page_size,
        total=result.total,
    )


@router.get("/{artifact_id}", response_model=IntelligenceItem)
def get_intelligence(
    artifact_id: str,
    db: Session = Depends(get_db),
) -> IntelligenceItem:
    repo = IntelligenceQueryRepository(db)
    record = repo.get_by_artifact_id(artifact_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Intelligence record not found")
    return _to_item(record)
