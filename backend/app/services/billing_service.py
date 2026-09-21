from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timedelta
from uuid import uuid4

import razorpay
import structlog
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.subscription import Subscription
from app.models.user import User

log = structlog.get_logger()

PLAN_INTERVAL_DAYS = 30

# "starter" isn't listed here — it's the free default (see User.plan) and has
# no checkout flow. "enterprise" is sold off-platform via a contact-sales
# form, not through Razorpay, so it isn't listed either.
PLANS = {
    "professional": {
        "id": "professional",
        "name": "Professional",
        "amount_paise": 99900,  # ₹999/month
        "amount_display": "₹999/month",
        "interval_days": PLAN_INTERVAL_DAYS,
        "features": [
            "Unlimited AI match scoring",
            "Email + in-app deadline alerts",
            "Proposal drafting assistant",
            "Full tender history & analytics",
        ],
    },
}


def _client() -> razorpay.Client:
    settings = get_settings()
    if not settings.razorpay_key_id or not settings.razorpay_key_secret:
        raise RuntimeError("Razorpay keys are not configured")
    client = razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))
    return client


def get_plan(plan_id: str) -> dict:
    plan = PLANS.get(plan_id)
    if not plan:
        raise ValueError(f"Unknown plan: {plan_id}")
    return plan


def create_order(db: Session, user_id: str, plan_id: str) -> dict:
    """Create a Razorpay order for a plan purchase/renewal."""
    plan = get_plan(plan_id)
    client = _client()

    order = client.order.create({
        "amount": plan["amount_paise"],
        "currency": "INR",
        "receipt": f"bidsight-{user_id[:16]}-{uuid4().hex[:8]}",
        "notes": {"user_id": user_id, "plan": plan_id},
    })

    sub = Subscription(
        id=str(uuid4()),
        user_id=user_id,
        plan=plan_id,
        status="created",
        amount_paise=plan["amount_paise"],
        razorpay_order_id=order["id"],
    )
    db.add(sub)
    db.commit()

    settings = get_settings()
    return {
        "order_id": order["id"],
        "amount_paise": plan["amount_paise"],
        "currency": "INR",
        "razorpay_key_id": settings.razorpay_key_id,
        "plan": plan_id,
    }


def verify_and_activate(
    db: Session,
    user_id: str,
    order_id: str,
    payment_id: str,
    signature: str,
) -> Subscription:
    """Verify a Razorpay checkout signature and activate the subscription."""
    settings = get_settings()
    expected = hmac.new(
        key=settings.razorpay_key_secret.encode(),
        msg=f"{order_id}|{payment_id}".encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        raise ValueError("Signature verification failed")

    sub = (
        db.query(Subscription)
        .filter(Subscription.razorpay_order_id == order_id, Subscription.user_id == user_id)
        .first()
    )
    if not sub:
        raise ValueError("No matching order for this user")

    _activate(db, sub, payment_id)
    return sub


def _activate(db: Session, sub: Subscription, payment_id: str) -> None:
    sub.status = "active"
    sub.razorpay_payment_id = payment_id
    sub.current_period_end = datetime.utcnow() + timedelta(days=PLAN_INTERVAL_DAYS)
    db.add(sub)

    user = db.query(User).filter(User.id == sub.user_id).first()
    if user:
        user.plan = sub.plan
        db.add(user)

    db.commit()
    log.info("subscription_activated", user_id=sub.user_id, plan=sub.plan)


def verify_webhook_signature(body: bytes, signature: str) -> bool:
    settings = get_settings()
    if not settings.razorpay_webhook_secret:
        return False
    expected = hmac.new(
        key=settings.razorpay_webhook_secret.encode(),
        msg=body,
        digestmod=hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def handle_webhook_event(db: Session, event: dict) -> None:
    """Handle a verified Razorpay webhook event (defense-in-depth vs. client-side verify)."""
    event_type = event.get("event")
    if event_type != "payment.captured":
        return

    payment = event["payload"]["payment"]["entity"]
    order_id = payment.get("order_id")
    payment_id = payment.get("id")
    if not order_id:
        return

    sub = db.query(Subscription).filter(Subscription.razorpay_order_id == order_id).first()
    if not sub or sub.status == "active":
        return  # unknown order, or already activated via the client-side verify path

    _activate(db, sub, payment_id)


def get_status(db: Session, user_id: str) -> dict:
    sub = (
        db.query(Subscription)
        .filter(Subscription.user_id == user_id, Subscription.status == "active")
        .order_by(Subscription.current_period_end.desc())
        .first()
    )
    if not sub:
        return {"plan": "starter", "status": "none", "current_period_end": None, "is_active": False}

    is_active = bool(sub.current_period_end and sub.current_period_end > datetime.utcnow())
    if not is_active:
        sub.status = "expired"
        db.commit()
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.plan = "starter"
            db.commit()

    return {
        "plan": sub.plan if is_active else "starter",
        "status": sub.status if is_active else "expired",
        "current_period_end": sub.current_period_end,
        "is_active": is_active,
    }
