import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.bid import Bid
from app.models.tender import Tender
from app.models.user import User  # needed for FK resolution
from app.schemas.bid import BidCreate, BidUpdate, BidResponse

router = APIRouter(prefix="/bids", tags=["bids"])

VALID_STAGES = ["new", "interested", "evaluating", "drafting", "submitted", "won", "lost"]


def _enrich_bid(bid: Bid, db: Session) -> dict:
    """Add tender details to bid response."""
    tender = db.query(Tender).filter(Tender.id == bid.tender_id).first()
    return {
        "id": bid.id,
        "user_id": bid.user_id,
        "tender_id": bid.tender_id,
        "stage": bid.stage,
        "match_score": bid.match_score,
        "notes": bid.notes,
        "created_at": bid.created_at,
        "updated_at": bid.updated_at,
        "tender_title": tender.title if tender else None,
        "tender_authority": tender.authority if tender else None,
        "tender_deadline": tender.deadline if tender else None,
        "tender_budget_raw": tender.budget_raw if tender else None,
        "tender_source": tender.source if tender else None,
    }


@router.get("/", response_model=list[BidResponse])
def list_bids(
    stage: str = None,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Get all bids for the user, optionally filtered by stage."""
    query = db.query(Bid).filter(Bid.user_id == user_id)
    if stage:
        query = query.filter(Bid.stage == stage)
    bids = query.order_by(Bid.updated_at.desc()).all()
    return [_enrich_bid(b, db) for b in bids]


@router.post("/", response_model=BidResponse)
def create_bid(
    data: BidCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Add a tender to the bid pipeline."""
    # Check tender exists
    tender = db.query(Tender).filter(Tender.id == data.tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    # Check not already in pipeline
    existing = db.query(Bid).filter(
        Bid.user_id == user_id,
        Bid.tender_id == data.tender_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tender already in pipeline")

    bid = Bid(
        id=str(uuid.uuid4()),
        user_id=user_id,
        tender_id=data.tender_id,
        stage=data.stage,
        match_score=tender.match_score,
        notes=data.notes,
    )
    db.add(bid)
    db.commit()
    db.refresh(bid)
    return _enrich_bid(bid, db)


@router.patch("/{bid_id}", response_model=BidResponse)
def update_bid(
    bid_id: str,
    data: BidUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Update bid stage or notes."""
    bid = db.query(Bid).filter(
        Bid.id == bid_id,
        Bid.user_id == user_id,
    ).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")

    if data.stage:
        if data.stage not in VALID_STAGES:
            raise HTTPException(status_code=400, detail=f"Invalid stage. Must be one of: {VALID_STAGES}")
        bid.stage = data.stage
    if data.notes is not None:
        bid.notes = data.notes

    db.commit()
    db.refresh(bid)
    return _enrich_bid(bid, db)


@router.delete("/{bid_id}")
def delete_bid(
    bid_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Remove a tender from the pipeline."""
    bid = db.query(Bid).filter(
        Bid.id == bid_id,
        Bid.user_id == user_id,
    ).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")

    db.delete(bid)
    db.commit()
    return {"status": "deleted"}


@router.get("/pipeline/summary")
def pipeline_summary(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Get count of bids per stage."""
    bids = db.query(Bid).filter(Bid.user_id == user_id).all()
    summary = {stage: 0 for stage in VALID_STAGES}
    for bid in bids:
        if bid.stage in summary:
            summary[bid.stage] += 1
    return summary