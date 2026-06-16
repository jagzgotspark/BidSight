from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime, timedelta

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.tender import Tender
from app.models.bid import Bid

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
def get_overview(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Full analytics overview for the dashboard."""

    # Total tenders
    total_tenders = db.query(Tender).count()

    # By source
    by_source = db.query(
        Tender.source,
        func.count(Tender.id).label("count")
    ).group_by(Tender.source).all()

    # By category
    by_category = db.query(
        Tender.category,
        func.count(Tender.id).label("count")
    ).group_by(Tender.category).order_by(func.count(Tender.id).desc()).all()

    # Match score distribution
    scored = db.query(Tender).filter(Tender.match_score.isnot(None)).all()
    score_dist = {"high": 0, "medium": 0, "low": 0, "unscored": 0}
    for t in scored:
        if t.match_score >= 70:
            score_dist["high"] += 1
        elif t.match_score >= 50:
            score_dist["medium"] += 1
        else:
            score_dist["low"] += 1
    score_dist["unscored"] = total_tenders - len(scored)

    # Pipeline by stage
    bids = db.query(
        Bid.stage,
        func.count(Bid.id).label("count")
    ).filter(Bid.user_id == user_id).group_by(Bid.stage).all()

    pipeline = {b.stage: b.count for b in bids}

    # Tenders scraped last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent = db.query(
        func.date(Tender.created_at).label("date"),
        func.count(Tender.id).label("count")
    ).filter(
        Tender.created_at >= seven_days_ago
    ).group_by(
        func.date(Tender.created_at)
    ).order_by(
        func.date(Tender.created_at)
    ).all()

    # Active vs closed
    active = db.query(Tender).filter(Tender.status == "active").count()
    closed = total_tenders - active

    # Average match score
    avg_score = db.query(func.avg(Tender.match_score)).filter(
        Tender.match_score.isnot(None)
    ).scalar()

    return {
        "total_tenders": total_tenders,
        "active_tenders": active,
        "closed_tenders": closed,
        "avg_match_score": round(float(avg_score), 1) if avg_score else 0,
        "by_source": [{"source": r.source, "count": r.count} for r in by_source],
        "by_category": [{"category": r.category, "count": r.count} for r in by_category],
        "score_distribution": score_dist,
        "pipeline": pipeline,
        "tenders_over_time": [
            {"date": str(r.date), "count": r.count} for r in recent
        ],
    }