import uuid
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.company_profile import CompanyProfile
from app.models.tender import Tender
from app.schemas.profile import (
    CompanyProfileCreate,
    CompanyProfileResponse,
    MatchScoreResponse,
)
from app.services.match_service import score_all_tenders, score_tender

router = APIRouter(prefix="/match", tags=["match"])


@router.post("/profile", response_model=CompanyProfileResponse)
def create_or_update_profile(
    data: CompanyProfileCreate,
    user_id: str = "demo_user",  # Replace with Clerk auth later
    db: Session = Depends(get_db),
):
    """Create or update a company profile."""
    profile = db.query(CompanyProfile).filter(
        CompanyProfile.user_id == user_id
    ).first()

    if profile:
        for key, value in data.model_dump().items():
            setattr(profile, key, value)
    else:
        profile = CompanyProfile(
            id=str(uuid.uuid4()),
            user_id=user_id,
            **data.model_dump(),
        )
        db.add(profile)

    db.commit()
    db.refresh(profile)
    return profile


@router.get("/profile", response_model=CompanyProfileResponse)
def get_profile(
    user_id: str = "demo_user",
    db: Session = Depends(get_db),
):
    """Get the current user's company profile."""
    profile = db.query(CompanyProfile).filter(
        CompanyProfile.user_id == user_id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.get("/score", response_model=list[MatchScoreResponse])
def get_match_scores(
    user_id: str = "demo_user",
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """Score all active tenders against the user's company profile."""
    profile = db.query(CompanyProfile).filter(
        CompanyProfile.user_id == user_id
    ).first()
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Set up your company profile first at POST /api/v1/match/profile"
        )

    tenders = (
        db.query(Tender)
        .filter(Tender.status == "active")
        .order_by(Tender.created_at.desc())
        .limit(limit)
        .all()
    )

    if not tenders:
        return []

    results = asyncio.run(score_all_tenders(tenders, profile, limit=limit))
    return results

@router.post("/score/{tender_id}")
async def score_single_tender(
    tender_id: str,
    user_id: str = "demo_user",
    db: Session = Depends(get_db),
):
    """Score one tender against the profile and persist the result."""
    profile = db.query(CompanyProfile).filter(
        CompanyProfile.user_id == user_id
    ).first()
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Set up your company profile first at POST /api/v1/match/profile",
        )

    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    if tender.match_score is not None:
        return {
            "tender_id": tender.id,
            "match_score": tender.match_score,
            "match_reasoning": tender.match_reasoning,
            "cached": True,
        }

    try:
        result = await score_tender(tender, profile)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Scoring failed: {exc}")

    tender.match_score = result["score"]
    tender.match_reasoning = result.get("reasoning", "")
    db.commit()

    return {
        "tender_id": tender.id,
        "match_score": tender.match_score,
        "match_reasoning": tender.match_reasoning,
        "cached": False,
    }