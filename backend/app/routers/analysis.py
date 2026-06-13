import io
import json

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.tender import Tender
from app.services.document_analysis_service import analyze_document

router = APIRouter(prefix="/analysis", tags=["analysis"])


def _extract_pdf_text(raw: bytes) -> str:
    reader = PdfReader(io.BytesIO(raw))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


@router.post("/document")
async def analyze(
    file: UploadFile = File(...),
    tender_id: str | None = Form(None),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    raw = await file.read()
    text = _extract_pdf_text(raw)
    if not text.strip():
        raise HTTPException(
            status_code=422,
            detail="Could not extract text (the PDF may be scanned images).",
        )

    tender = None
    tender_title = ""
    if tender_id:
        tender = db.query(Tender).filter(Tender.id == tender_id).first()
        if tender:
            tender_title = tender.title

    try:
        result = await analyze_document(text, tender_title)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI analysis failed: {exc}")

    if tender:
        tender.ai_analysis = json.dumps(result)
        tender.ai_summary = result.get("summary", "")
        risks = result.get("risks", [])
        tender.ai_risk = "; ".join(risks) if isinstance(risks, list) else str(risks)
        elig = result.get("eligibility_criteria", [])
        tender.ai_eligibility = "; ".join(elig) if isinstance(elig, list) else str(elig)
        tender.ai_processed = True
        db.commit()

    return result


@router.get("/{tender_id}")
def get_analysis(tender_id: str, db: Session = Depends(get_db)):
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    if not tender.ai_analysis:
        return {"analyzed": False}
    return {"analyzed": True, "analysis": json.loads(tender.ai_analysis)}