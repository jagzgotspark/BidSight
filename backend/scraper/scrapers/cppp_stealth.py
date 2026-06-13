from __future__ import annotations

"""
CPPP (Central Public Procurement Portal) stealth scraper.

Strategy (CAPTCHA-free):
  1. Load "Tenders by Organisation" — the org listing renders without solving
     the CAPTCHA, giving ~243 organisations each with a $DirectLink.
  2. Follow each org's drill-down link (also CAPTCHA-free) and parse its
     6-column tender table.
  3. Dedup via Redis fingerprints, save to PostgreSQL.

The sp= tokens in org links are session-bound, so we harvest and follow them
within the SAME browser run.

Run from backend/ in the scraper venv:
    source .venv-scraper/bin/activate
    python scraper/scrapers/cppp_stealth.py          # all orgs
    python scraper/scrapers/cppp_stealth.py 5         # first 5 orgs (dev)
"""

import asyncio
import os
import re
import sys
from datetime import datetime

# Make backend/ importable when run as a script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from playwright.async_api import async_playwright
from playwright_stealth import Stealth

from scraper.models.tender import Tender, TenderCategory, TenderSource, TenderStatus
from scraper.scrapers.gem import _classify  # shared category classifier
from scraper.dedup import Deduplicator
from app.database import SessionLocal
from app.services.tender_service import bulk_upsert_tenders

ORG_LIST_URL = (
    "https://eprocure.gov.in/eprocure/app"
    "?page=FrontEndTendersByOrganisation&service=page"
)
BASE = "https://eprocure.gov.in"


def _parse_cppp_date(raw: str):
    """Parse CPPP dates like '11-Jun-2026 05:20 PM'."""
    raw = (raw or "").strip()
    if not raw:
        return None
    for fmt in ("%d-%b-%Y %I:%M %p", "%d-%b-%Y %H:%M", "%d-%b-%Y"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


def _parse_title_cell(raw: str) -> tuple[str, str]:
    """
    The title cell looks like:
        [Construction of RCC wall ...] [RI_16/Bldg/26][2026_AMU_912648_1]
    First bracket = title, last bracket = tender ID.
    """
    groups = re.findall(r"\[([^\[\]]*)\]", raw or "")
    if not groups:
        clean = (raw or "").strip()
        return clean, clean[:40]
    title = groups[0].strip()
    tender_id = groups[-1].strip() if len(groups) > 1 else title[:40]
    return title, tender_id


async def harvest_org_links(page) -> list[dict]:
    """Return [{name, href}] for every organisation on the listing page."""
    return await page.evaluate(
        """
        () => {
          const out = [];
          const rows = document.querySelectorAll('table.list_table tr');
          for (const row of rows) {
            const link = row.querySelector('a[href*="DirectLink"]');
            if (!link) continue;
            const cells = row.querySelectorAll('td');
            let name = cells.length >= 2 ? cells[1].innerText.trim() : '';
            out.push({ name, href: link.getAttribute('href') });
          }
          return out;
        }
        """
    )


async def scrape_org(page, org: dict) -> list[Tender]:
    """Follow one org's drill-down link and parse its tender table."""
    url = org["href"]
    if url.startswith("/"):
        url = BASE + url

    await page.goto(url, wait_until="domcontentloaded", timeout=60000)
    await asyncio.sleep(2)

    rows = await page.evaluate(
        """
        () => {
          const out = [];
          const trs = document.querySelectorAll('table.list_table tr');
          for (const tr of trs) {
            const tds = tr.querySelectorAll('td');
            if (tds.length < 6) continue;
            out.push([...tds].map(td => td.innerText.trim()));
          }
          return out;
        }
        """
    )

    tenders: list[Tender] = []
    for cells in rows:
        # Skip header / non-data rows (S.No must be a number)
        if not cells[0].strip().isdigit():
            continue
        published_raw = cells[1]
        deadline_raw = cells[2]
        title_cell = cells[4]
        org_chain = cells[5]

        title, tender_id = _parse_title_cell(title_cell)
        if not title:
            continue

        try:
            tenders.append(
                Tender(
                    tender_id=tender_id,
                    source=TenderSource.CPPP,
                    title=title,
                    authority=org_chain or org["name"],
                    location="",
                    category=_classify(title),
                    budget_raw="",  # not exposed on the listing page
                    published_at=_parse_cppp_date(published_raw),
                    deadline=_parse_cppp_date(deadline_raw),
                    deadline_raw=deadline_raw,
                    status=TenderStatus.ACTIVE,
                    source_url=url,
                    eligibility_raw="",
                )
            )
        except Exception as exc:
            print(f"    ! row parse error: {exc}")

    return tenders


def _to_dict(t: Tender) -> dict:
    return {
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
    }


async def main(max_orgs: int = 250):
    async with async_playwright() as p:
        headless = os.getenv("SCRAPER_HEADLESS", "0") == "1"
        browser = await p.chromium.launch(headless=headless)
        page = await browser.new_page()
        await Stealth().apply_stealth_async(page)

        print("Loading organisation list...")
        await page.goto(ORG_LIST_URL, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(6)

        orgs = await harvest_org_links(page)
        print(f"Found {len(orgs)} organisations. Scraping up to {max_orgs}.\n")

        all_tenders: list[Tender] = []
        for i, org in enumerate(orgs[:max_orgs], start=1):
            print(f"[{i}/{min(len(orgs), max_orgs)}] {org['name'][:50]}")
            try:
                tenders = await scrape_org(page, org)
                print(f"    {len(tenders)} tenders")
                all_tenders.extend(tenders)
            except Exception as exc:
                print(f"    ! org failed: {exc}")
            await asyncio.sleep(2)  # be polite to the portal

        await browser.close()

    if not all_tenders:
        print("\nNo tenders scraped.")
        return

    # Dedup
    dedup = Deduplicator()
    new_tenders = [t for t in all_tenders if dedup.is_new(t.fingerprint)]
    print(f"\n{len(all_tenders)} scraped, {len(new_tenders)} new after dedup")

    if not new_tenders:
        print("Nothing new to save.")
        return

    # Save
    db = SessionLocal()
    try:
        result = bulk_upsert_tenders(db, [_to_dict(t) for t in new_tenders])
        print(f"Saved: {result['created']} new, {result['skipped']} skipped")
        for t in new_tenders:
            dedup.mark_seen(t.fingerprint)
    finally:
        db.close()

    print("\nDone.")


if __name__ == "__main__":
    max_orgs = int(sys.argv[1]) if len(sys.argv) > 1 else 250
    asyncio.run(main(max_orgs))