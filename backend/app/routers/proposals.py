import uuid
import asyncio
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.proposal import Proposal
from app.models.tender import Tender
from app.models.company_profile import CompanyProfile
from app.services.proposal_service import generate_proposal, extract_text_from_pdf

router = APIRouter(prefix="/proposals", tags=["proposals"])


@router.post("/generate")
async def generate_proposal_endpoint(
    tender_id: str = Form(...),
    past_projects: str = Form(default=""),
    additional_notes: str = Form(default=""),
    company_profile_pdf: Optional[UploadFile] = File(default=None),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Generate a full proposal for a tender.
    Accepts optional PDF upload for company profile.
    """
    # Get tender
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    # Get company profile
    profile = db.query(CompanyProfile).filter(
        CompanyProfile.user_id == user_id
    ).first()
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Set up your company profile first at POST /api/v1/match/profile"
        )

    # Extract PDF text if uploaded
    pdf_text = ""
    if company_profile_pdf and company_profile_pdf.filename:
        pdf_bytes = await company_profile_pdf.read()
        pdf_text = extract_text_from_pdf(pdf_bytes)

    # Generate proposal
    sections = await generate_proposal(
        tender_title=tender.title,
        tender_authority=tender.authority or "",
        tender_description=tender.description or "",
        tender_budget=tender.budget_raw or "",
        tender_deadline=tender.deadline_raw or "",
        company_name=profile.company_name,
        company_services=profile.services,
        company_tech_stack=profile.tech_stack,
        company_certifications=profile.certifications,
        company_team_size=profile.team_size,
        past_projects=past_projects,
        additional_notes=additional_notes,
        company_profile_text=pdf_text,
    )

    # Save to DB
    proposal = Proposal(
        id=str(uuid.uuid4()),
        user_id=user_id,
        tender_id=tender_id,
        company_profile_text=pdf_text,
        past_projects=past_projects,
        additional_notes=additional_notes,
        status="generated",
        **sections,
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)

    return {
        "id": proposal.id,
        "tender_title": tender.title,
        "tender_authority": tender.authority,
        **sections,
    }


@router.get("/{proposal_id}")
def get_proposal(proposal_id: str, db: Session = Depends(get_db)):
    """Get a saved proposal."""
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal


@router.get("/tender/{tender_id}")
def get_proposals_for_tender(tender_id: str, db: Session = Depends(get_db)):
    """Get all proposals for a tender."""
    proposals = db.query(Proposal).filter(
        Proposal.tender_id == tender_id
    ).order_by(Proposal.created_at.desc()).all()
    return proposals