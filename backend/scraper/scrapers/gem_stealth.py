from __future__ import annotations

"""
GeM Scraper — intercepts the /all-bids-data XHR call made by the browser.
No HTML parsing needed — we get clean JSON directly.
"""

import asyncio
import json
import os
import sys
import re
from datetime import datetime
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from playwright.async_api import async_playwright
from playwright_stealth import Stealth

from scraper.models.tender import Tender, TenderCategory, TenderSource, TenderStatus
from scraper.scrapers.gem import _classify, _parse_inr, _parse_date


async def scrape_gem_stealth(max_pages: int = 3) -> list[Tender]:
    all_tenders: list[Tender] = []
    api_responses: list[dict] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )

        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            locale="en-IN",
        )

        page = await context.new_page()
        await Stealth().apply_stealth_async(page)

        # Intercept the all-bids-data API response
        async def handle_response(response):
            if "all-bids-data" in response.url and response.status == 200:
                print(f"  Captured: {response.url}")
                try:
                    body = await response.json()
                    api_responses.append(body)
                except Exception as exc:
                    print(f"  Parse error: {exc}")

        page.on("response", handle_response)

        print("Opening GeM portal...")
        await page.goto(
            "https://bidplus.gem.gov.in/all-bids",
            wait_until="networkidle",
            timeout=60000,
        )
        await asyncio.sleep(5)

        # Parse page 1 from captured response
        if api_responses:
            tenders = _parse_api_response(api_responses[0])
            print(f"  Page 1: {len(tenders)} tenders")
            all_tenders.extend(tenders)
            api_responses.clear()

        # Navigate to subsequent pages by calling loadBids() via JS
        for page_num in range(2, max_pages + 1):
            print(f"  Loading page {page_num}...")
            await page.evaluate(f"window.currentPage = {page_num}; loadBids();")
            await asyncio.sleep(5)

            if api_responses:
                tenders = _parse_api_response(api_responses[0])
                print(f"  Page {page_num}: {len(tenders)} tenders")
                all_tenders.extend(tenders)
                api_responses.clear()
            else:
                print(f"  Page {page_num}: no response captured")
                break

        await browser.close()

    return all_tenders


def _parse_api_response(data: dict) -> list[Tender]:
    docs = (
        data.get("response", {}).get("response", {}).get("docs", [])
        or data.get("docs", [])
        or []
    )

    tenders = []
    for doc in docs:
        try:
            tenders.append(_normalise_doc(doc))
        except Exception as exc:
            print(f"  Doc error: {exc}")
    return tenders


def _normalise_doc(doc: dict) -> Tender:
    def first(val):
        if isinstance(val, list):
            return val[0] if val else ""
        return val or ""

    bid_number = str(first(doc.get("b_bid_number", "")))
    title = str(first(doc.get("b_category_name") or doc.get("b_title", ""))).strip()
    authority = str(first(doc.get("b_ministry_name") or doc.get("b_dept_name", ""))).strip()
    location = str(first(doc.get("b_state", ""))).strip()
    deadline_raw = str(first(doc.get("b_bid_end_date") or doc.get("b_end_date", "")))
    published_raw = str(first(doc.get("b_publish_date") or doc.get("b_start_date", "")))
    budget_raw = str(first(doc.get("b_estimated_amount") or doc.get("b_total_value", "")))
    bid_id = str(first(doc.get("id") or doc.get("b_id", "")))
    source_url = f"https://bidplus.gem.gov.in/viewbid/{bid_number}" if bid_number else ""

    return Tender(
        tender_id=bid_number or bid_id or title[:40],
        source=TenderSource.GEM,
        title=title or f"GeM Bid {bid_number}",
        authority=authority,
        location=location,
        category=_classify(title),
        budget_max=_parse_inr(budget_raw),
        budget_raw=budget_raw,
        deadline=_parse_date(deadline_raw),
        deadline_raw=deadline_raw,
        published_at=_parse_date(published_raw),
        status=TenderStatus.ACTIVE,
        source_url=source_url,
    )


async def main():
    print("=" * 50)
    print("GeM Stealth Scraper")
    print("=" * 50)

    tenders = await scrape_gem_stealth(max_pages=2)

    if not tenders:
        print("\nNo tenders scraped.")
        return

    print(f"\n✓ Scraped {len(tenders)} tenders total")
    for t in tenders[:5]:
        print(f"  - {t.title[:60]}")
        print(f"    Budget: {t.budget_display} | Deadline: {t.deadline_raw}")

    # Save to DB
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

    from app.database import SessionLocal
    from app.services.tender_service import bulk_upsert_tenders
    from scraper.dedup import Deduplicator

    dedup = Deduplicator()
    new_tenders = [t for t in tenders if dedup.is_new(t.fingerprint)]
    print(f"\n{len(new_tenders)} new tenders to save")

    if not new_tenders:
        print("All already in DB.")
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
        print(f"✓ Saved {result['created']} new, {result['skipped']} skipped")
        for t in new_tenders:
            dedup.mark_seen(t.fingerprint)
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())