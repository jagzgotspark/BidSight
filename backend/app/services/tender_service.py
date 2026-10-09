from datetime import datetime

from sqlalchemy.orm import Session
from app.models.tender import Tender


def upsert_tender(db: Session, tender_data: dict) -> tuple[Tender, bool]:
    """
    Insert a tender if it doesn't exist yet.
    Returns (tender, created) where created=True means it was new.
    """
    existing = db.query(Tender).filter(
        Tender.id == tender_data["id"]
    ).first()

    if existing:
        return existing, False

    tender = Tender(**tender_data)
    db.add(tender)
    db.commit()
    db.refresh(tender)
    return tender, True


def bulk_upsert_tenders(db: Session, tenders: list[dict]) -> dict:
    """
    Bulk insert new tenders, skip duplicates.
    Returns a summary dict.
    """
    created = 0
    skipped = 0

    for tender_data in tenders:
        _, was_created = upsert_tender(db, tender_data)
        if was_created:
            created += 1
        else:
            skipped += 1

    return {"created": created, "skipped": skipped, "total": len(tenders)}


def tender_ids_missing_budget(db: Session, ids: list[str]) -> set[str]:
    """
    Of the given tender ids, return those that still need a budget lookup:
    not saved yet, or saved but never checked (budget_raw blank).
    """
    if not ids:
        return set()
    checked = {
        row.id
        for row in db.query(Tender.id).filter(
            Tender.id.in_(ids),
            Tender.budget_raw.isnot(None),
            Tender.budget_raw != "",
        )
    }
    return set(ids) - checked


def update_tender_budgets(db: Session, budgets: dict[str, tuple[str, float | None]]) -> int:
    """Set budget_raw/budget_max on existing tenders. Returns count updated."""
    updated = 0
    for tender_id, (budget_raw, budget_max) in budgets.items():
        updated += (
            db.query(Tender)
            .filter(Tender.id == tender_id)
            .update({"budget_raw": budget_raw, "budget_max": budget_max}, synchronize_session=False)
        )
    db.commit()
    return updated


def expire_stale_tenders(db: Session) -> int:
    """Mark active tenders whose deadline has passed as closed. Returns count updated."""
    updated = (
        db.query(Tender)
        .filter(Tender.status == "active", Tender.deadline < datetime.utcnow())
        .update({"status": "closed"}, synchronize_session=False)
    )
    db.commit()
    return updated