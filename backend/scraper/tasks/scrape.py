def _save_tenders_to_db(tenders: list[Tender]) -> int:
    """
    Bulk-insert tenders. Returns count of rows inserted.

    TODO: replace this stub with your actual SQLAlchemy session:

        from scraper.db import get_session
        from scraper.models.orm import TenderORM

        with get_session() as session:
            objs = [TenderORM(**t.model_dump(exclude={'raw_html'})) for t in tenders]
            session.bulk_save_objects(objs, update_changed_only=False)
            session.commit()
        return len(objs)
    """
    for tender in tenders:
        log.info(
            "tender_saved_stub",
            source=tender.source.value,
            tender_id=tender.tender_id,
            title=tender.title[:60],
            deadline=tender.deadline_raw,
            budget=tender.budget_display,
        )
    return len(tenders)