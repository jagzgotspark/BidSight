"""
Run the scraper manually.
Usage: python run_scraper.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from scraper.scrapers.gem import GeMScraper
from scraper.scrapers.cppp import CPPPScraper
from scraper.dedup import Deduplicator
from app.database import SessionLocal
from app.services.tender_service import bulk_upsert_tenders


async def run(scraper_cls, name: str, max_pages: int = 2):
    print(f"\n{'='*50}\nRunning {name} (max {max_pages} pages)\n{'='*50}")
    tenders = []
    async with scraper_cls(max_pages=max_pages) as scraper:
        async for tender in scraper.scrape():
            tenders.append(tender)
            print(f"  {tender.title[:70]}")
            print(f"  Budget: {tender.budget_display} | Deadline: {tender.deadline_raw}\n")

    if not tenders:
        print(f"No tenders from {name}")
        return

    dedup = Deduplicator()
    new_tenders = [t for t in tenders if dedup.is_new(t.fingerprint)]
    print(f"{len(tenders)} scraped → {len(new_tenders)} new")

    if not new_tenders:
        print("Nothing new to save.")
        return

    tender_dicts = [{
        "id": t.fingerprint,
        "tender_id": t.tender_id,
        "source": t.source.value,
        "title": t.title,
        "description": t.description,
        "authority": t.authority,
        "location": t.location,
        "category": t.category.value,
        "budget_min": t.budget_min,
        "budget_max": t.budget_max,
        "budget_raw": t.budget_raw,
        "published_at": t.published_at,
        "deadline": t.deadline,
        "deadline_raw": t.deadline_raw,
        "status": t.status.value,
        "source_url": t.source_url,
        "eligibility_raw": t.eligibility_raw,
        "scraped_at": t.scraped_at,
    } for t in new_tenders]

    db = SessionLocal()
    try:
        result = bulk_upsert_tenders(db, tender_dicts)
        print(f"✓ Saved {result['created']} new tenders ({result['skipped']} skipped)")
        for t in new_tenders:
            dedup.mark_seen(t.fingerprint)
    finally:
        db.close()


async def main():
    await run(CPPPScraper, "CPPP", max_pages=2)
    print("\nDone!")

if __name__ == "__main__":
    asyncio.run(main())