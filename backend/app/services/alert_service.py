from __future__ import annotations
import asyncio
from datetime import datetime, timedelta
import math
import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
from uuid import uuid4

import structlog
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.bid import Bid
from app.models.tender import Tender

log = structlog.get_logger()

THRESHOLDS = [30, 14, 7, 3, 1]
ACTIVE_STAGES = ("new", "interested", "evaluating", "drafting", "submitted")


def _maybe_send_email(db: Session, alert: Alert) -> bool:
    """Send an email if SMTP is configured. Otherwise no-op (in-app only)."""
    if os.getenv("ALERTS_EMAIL_ENABLED", "0") != "1":
        return False
    host = os.getenv("SMTP_HOST")
    if not host:
        return False

    from app.models.user import User
    user = db.query(User).filter(User.id == alert.user_id).first()
    if not user or not user.email:
        return False

    try:
        msg = EmailMessage()
        msg["Subject"] = f"BidSight: tender closing in {alert.days_left} days"
        msg["From"] = os.getenv("SMTP_FROM", os.getenv("SMTP_USER", "alerts@bidsight.app"))
        msg["To"] = user.email
        msg.set_content(
            f"{alert.message}\n\nDeadline: {alert.deadline}\n\n"
            "Open BidSight to act on it."
        )
        with smtplib.SMTP(host, int(os.getenv("SMTP_PORT", "587"))) as s:
            s.starttls()
            smtp_user, smtp_pwd = os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD")
            if smtp_user and smtp_pwd:
                s.login(smtp_user, smtp_pwd)
            s.send_message(msg)
        return True
    except Exception as exc:
        log.warning("alert_email_failed", error=str(exc))
        return False


def scan_and_create_alerts(db: Session) -> dict:
    """
    Scan tracked bids in active stages, compare each tender's deadline against
    the reminder buckets, and create one alert per newly-crossed bucket.
    """
    now = datetime.utcnow()
    bids = db.query(Bid).filter(Bid.stage.in_(ACTIVE_STAGES)).all()

    created = 0
    for bid in bids:
        tender = db.query(Tender).filter(Tender.id == bid.tender_id).first()
        if not tender or not tender.deadline:
            continue

        secs = (tender.deadline - now).total_seconds()
        if secs < 0:
            continue  # already closed
        days_left = max(0, math.ceil(secs / 86400))

        reached = [t for t in THRESHOLDS if days_left <= t]
        if not reached:
            continue
        tightest = min(reached)

        # Already alerted this bid at this (or a tighter) bucket?
        already = (
            db.query(Alert)
            .filter(Alert.bid_id == bid.id, Alert.threshold == tightest)
            .first()
        )
        if already:
            continue

        plural = "s" if days_left != 1 else ""
        alert = Alert(
            id=str(uuid4()),
            user_id=bid.user_id,
            bid_id=bid.id,
            tender_id=tender.id,
            tender_title=tender.title,
            deadline=tender.deadline,
            days_left=days_left,
            threshold=tightest,
            message=f'"{tender.title[:80]}" closes in {days_left} day{plural}',
            channel="in_app",
        )
        db.add(alert)
        alert.emailed = _maybe_send_email(db, alert)
        created += 1

    db.commit()
    return {"bids_checked": len(bids), "alerts_created": created}

MATCH_THRESHOLD = 70


async def create_match_alerts(
    db: Session,
    user_id: str = "demo_user",
    threshold: int = MATCH_THRESHOLD,
    since_days: int = 7,
) -> dict:
    """Score recent unscored tenders and alert on high-fit new matches."""
    from app.models.company_profile import CompanyProfile
    from app.services.match_service import score_tender

    profile = db.query(CompanyProfile).filter(CompanyProfile.user_id == user_id).first()
    if not profile:
        return {"error": "No company profile set up yet."}

    cutoff = datetime.utcnow() - timedelta(days=since_days)
    tenders = (
        db.query(Tender)
        .filter(Tender.status == "active", Tender.created_at >= cutoff)
        .all()
    )

    # Ensure recent tenders are scored
    scored = 0
    for t in tenders:
        if t.match_score is None:
            try:
                result = await score_tender(t, profile)
                t.match_score = result["score"]
                t.match_reasoning = result.get("reasoning", "")
                scored += 1
            except Exception as exc:
                log.warning("match_alert_scoring_failed", error=str(exc))
            await asyncio.sleep(0.5)
    db.commit()

    # Create alerts for high matches (deduped via bid_id="match:<id>")
    now = datetime.utcnow()
    created = 0
    for t in tenders:
        if t.match_score is None or t.match_score < threshold:
            continue

        bid_key = f"match:{t.id}"
        exists = (
            db.query(Alert)
            .filter(Alert.bid_id == bid_key, Alert.threshold == threshold)
            .first()
        )
        if exists:
            continue

        days_left = None
        if t.deadline:
            secs = (t.deadline - now).total_seconds()
            days_left = max(0, math.ceil(secs / 86400)) if secs > 0 else 0

        alert = Alert(
            id=str(uuid4()),
            user_id=user_id,
            bid_id=bid_key,
            tender_id=t.id,
            tender_title=t.title,
            deadline=t.deadline,
            days_left=days_left,
            threshold=threshold,
            kind="match",
            score=t.match_score,
            message=f'New {t.match_score}% match: "{t.title[:80]}"',
            channel="in_app",
        )
        db.add(alert)
        alert.emailed = _maybe_send_email(db, alert)
        created += 1

    db.commit()
    return {"recent_tenders": len(tenders), "scored": scored, "match_alerts_created": created}