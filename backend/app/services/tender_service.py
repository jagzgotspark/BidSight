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