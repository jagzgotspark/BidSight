from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.alert import Alert
from app.schemas.alert import AlertResponse

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/", response_model=list[AlertResponse])
def list_alerts(unread_only: bool = False, db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    q = db.query(Alert).filter(Alert.user_id == user_id)
    if unread_only:
        q = q.filter(Alert.is_read == False)  # noqa: E712
    return q.order_by(Alert.created_at.desc()).limit(100).all()


@router.get("/unread-count")
def unread_count(db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    n = db.query(Alert).filter(Alert.user_id == user_id, Alert.is_read == False).count()  # noqa: E712
    return {"unread": n}


@router.post("/{alert_id}/read")
def mark_read(alert_id: str, db: Session = Depends(get_db)):
    a = db.query(Alert).filter(Alert.id == alert_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Alert not found")
    a.is_read = True
    db.commit()
    return {"ok": True}


@router.post("/read-all")
def mark_all_read(db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    db.query(Alert).filter(Alert.user_id == user_id, Alert.is_read == False).update(  # noqa: E712
        {"is_read": True}
    )
    db.commit()
    return {"ok": True}


@router.post("/scan")
def scan_now(db: Session = Depends(get_db)):
    """Manually trigger a deadline scan (same logic the Celery task runs)."""
    from app.services.alert_service import scan_and_create_alerts
    return scan_and_create_alerts(db)

@router.post("/scan-matches")
def scan_matches_now(threshold: int = 70, db: Session = Depends(get_db)):
    """Manually run the new-match scan (same logic the Celery task runs)."""
    import asyncio
    from app.services.alert_service import create_match_alerts
    return asyncio.run(create_match_alerts(db, threshold=threshold))