from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.tender import Tender
from app.schemas.tender import TenderResponse, TenderListResponse

router = APIRouter(prefix="/tenders", tags=["tenders"])


@router.get("/", response_model=TenderListResponse)
def list_tenders(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    source: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = "active",
    location: Optional[str] = None,
    min_budget: Optional[float] = None,
    max_budget: Optional[float] = None,
    closing_in_days: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    scored_only: bool = False,
):
    """
    List tenders with filters.
    Supports: source, category, status, location, budget range,
              deadline filter, and keyword search.
    """
    query = db.query(Tender)

    # Filters
    if source:
        query = query.filter(Tender.source == source)
    if category:
        query = query.filter(Tender.category == category)
    if status:
        query = query.filter(Tender.status == status)
    if location:
        query = query.filter(Tender.location.ilike(f"%{location}%"))
    if min_budget:
        query = query.filter(Tender.budget_max >= min_budget)
    if max_budget:
        query = query.filter(Tender.budget_max <= max_budget)
    if scored_only:
        query = query.filter(Tender.match_score.isnot(None))
    if closing_in_days:
        cutoff = datetime.utcnow() + timedelta(days=closing_in_days)
        query = query.filter(
            and_(Tender.deadline <= cutoff, Tender.deadline >= datetime.utcnow())
        )
    if search:
        query = query.filter(
            or_(
                Tender.title.ilike(f"%{search}%"),
                Tender.description.ilike(f"%{search}%"),
                Tender.authority.ilike(f"%{search}%"),
            )
        )

    # Total count before pagination
    total = query.count()

    # Pagination — newest first
    offset = (page - 1) * per_page
    items = (
        query.order_by(Tender.created_at.desc())
        .offset(offset)
        .limit(per_page)
        .all()
    )

    return TenderListResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=-(-total // per_page),  # ceiling division
    )


@router.get("/{tender_id}", response_model=TenderResponse)
def get_tender(tender_id: str, db: Session = Depends(get_db)):
    """Get a single tender by its ID (fingerprint)."""
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    return tender


@router.get("/source/{source}", response_model=TenderListResponse)
def tenders_by_source(
    source: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get tenders filtered by source portal (gem or cppp)."""
    query = db.query(Tender).filter(Tender.source == source)
    total = query.count()
    offset = (page - 1) * per_page
    items = (
        query.order_by(Tender.deadline.asc())
        .offset(offset)
        .limit(per_page)
        .all()
    )
    return TenderListResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=-(-total // per_page),
    )


@router.get("/closing/soon", response_model=TenderListResponse)
def closing_soon(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
):
    """Get tenders closing within N days. Default: 7 days."""
    cutoff = datetime.utcnow() + timedelta(days=days)
    query = db.query(Tender).filter(
        and_(
            Tender.deadline <= cutoff,
            Tender.deadline >= datetime.utcnow(),
            Tender.status == "active",
        )
    )
    total = query.count()
    items = query.order_by(Tender.deadline.asc()).limit(50).all()
    return TenderListResponse(
        items=items,
        total=total,
        page=1,
        per_page=50,
        pages=1,
    )