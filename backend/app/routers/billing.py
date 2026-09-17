from fastapi import APIRouter, Depends, HTTPException, Request

from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.billing import (
    CheckoutRequest,
    CheckoutResponse,
    PlanOut,
    SubscriptionStatus,
    VerifyPaymentRequest,
)
from app.services import billing_service

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/plans", response_model=list[PlanOut])
def list_plans():
    return list(billing_service.PLANS.values())


@router.get("/status", response_model=SubscriptionStatus)
def status(db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    return billing_service.get_status(db, user_id)


@router.post("/checkout", response_model=CheckoutResponse)
def checkout(
    data: CheckoutRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    try:
        return billing_service.create_order(db, user_id, data.plan)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.post("/verify")
def verify(
    data: VerifyPaymentRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    try:
        sub = billing_service.verify_and_activate(
            db, user_id, data.razorpay_order_id, data.razorpay_payment_id, data.razorpay_signature
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"ok": True, "plan": sub.plan, "current_period_end": sub.current_period_end}


@router.post("/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)):
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")

    if not billing_service.verify_webhook_signature(body, signature):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    event = await request.json()
    billing_service.handle_webhook_event(db, event)
    return {"ok": True}
