from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.services.billing_service import get_status

STARTER_DAILY_SCORE_LIMIT = 10


def require_professional_plan(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> str:
    """FastAPI dependency: 402s unless the user has an active paid plan."""
    status = get_status(db, user_id)
    if not status["is_active"]:
        raise HTTPException(
            status_code=402,
            detail="This feature requires the Professional plan. Upgrade at /dashboard/billing.",
        )
    return user_id
