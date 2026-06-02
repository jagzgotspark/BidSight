from __future__ import annotations

"""
CPPP (Central Public Procurement Portal) Scraper
=================================================
CPPP is an NIC-run portal at https://eprocure.gov.in/cppp/

It does NOT expose a clean JSON API — tenders are in HTML tables
with server-side pagination via form POST.

Strategy:
  1. GET /latestactivetenders — extract CSRF / view state
  2. POST with page number to get paginated tender rows
  3. Parse HTML table rows into Tender objects
  4. For each tender, optionally fetch the detail page for full text

Playwright is used for the initial page (JS-rendered tender counts),
then httpx takes over for paginated POSTs once we have the session cookie.
"""

import re
from datetime import datetime
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from scraper.models.tender import Tender, TenderCategory, TenderSource, TenderStatus
from scraper.scrapers.base import BaseScraper
from scraper.scrapers.gem import _classify, _parse_date, _parse_inr  # shared utils

# CPPP base
_BASE = "https://eprocure.gov.in"
_LIST_URL = f"{_BASE}/cppp/latestactivetenders"
_DETAIL_BASE = f"{_BASE}/eprocure/app"


class CPPPScraper(BaseScraper):
    """
    Scrapes active tenders from CPPP (Central Public Procurement Portal).

    CPPP paginates via GET with `?page=N`. Each page returns an HTML table
    with up to 20 tenders. We parse each row and yield normalised Tenders.

    The portal occasionally returns a CAPTCHA page — we detect this and stop
    gracefully rather than hammering the server.
    """

    source_name = "cppp"
    base_url = _BASE
    page_delay_seconds = 3.0          # CPPP is sensitive to fast requests

    _LIST_URL = _LIST_URL

    # CPPP uses GET pagination: ?page=1&sortBy=&sortOrder=
    _PAGE_PARAM = "page"

    async def _fetch_listing_page(self, page: int) -> httpx.Response:
        params = {
            "page": page,
            "sortBy": "publishing_date",
            "sortOrder": "desc",
        }
        return await self._client.get(self._LIST_URL, params=params)

    def _parse_listing(self, response: httpx.Response) -> list[Tender]:
        html = response.text

        # Detect CAPTCHA / bot protection
        if "captcha" in html.lower() or "robot" in html.lower():
            self.log.warning("captcha_detected", url=str(response.url))
            return []

        soup = BeautifulSoup(html, "lxml")
        tenders: list[Tender] = []

        # CPPP main table — columns vary slightly by page but follow this pattern:
        # | Tender ID | Tender Title | Organisation | Published | Closing | Value |
        table = soup.select_one("table#table, table.list_table, table.tablebg")
        if not table:
            self.log.warning("table_not_found", url=str(response.url))
            return []

        rows = table.select("tr")[1:]  # skip header row

        for row in rows:
            try:
                tender = self._parse_row(row)
                if tender:
                    tenders.append(tender)
            except Exception as exc:
                self.log.warning("row_parse_error", error=str(exc))

        return tenders

    def _parse_row(self, row) -> Optional[Tender]:
        cells = row.select("td")
        if len(cells) < 4:
            return None

        # Try to extract the detail-page link and tender ID from first anchor
        link_el = row.select_one("a[href]")
        href = link_el["href"] if link_el else ""
        source_url = href if href.startswith("http") else (_BASE + href if href else "")

        # Extract tender ID from URL or text
        tender_id = ""
        id_match = re.search(r"(?:tenderID|tid|ref|id)[=\/]([A-Z0-9\-\/]+)", href, re.I)
        if id_match:
            tender_id = id_match.group(1)

        # Cell content — CPPP table structure (0-indexed):
        # 0: S.No  1: Tender ID  2: Tender Title  3: Organisation
        # 4: Published Date  5: Closing Date  6: Tender Value
        # (Some pages have fewer columns; we handle both layouts)
        def cell_text(idx: int) -> str:
            if idx < len(cells):
                return cells[idx].get_text(strip=True)
            return ""

        if len(cells) >= 7:
            # Full layout
            tender_id = tender_id or cell_text(1)
            title = cell_text(2)
            authority = cell_text(3)
            published_raw = cell_text(4)
            deadline_raw = cell_text(5)
            budget_raw = cell_text(6)
        elif len(cells) >= 5:
            # Compact layout
            tender_id = tender_id or cell_text(0)
            title = cell_text(1)
            authority = cell_text(2)
            deadline_raw = cell_text(3)
            budget_raw = cell_text(4)
            published_raw = ""
        else:
            return None

        if not title or title in ("-", "N/A", ""):
            return None

        return Tender(
            tender_id=tender_id or title[:40],
            source=TenderSource.CPPP,
            title=title,
            authority=authority,
            category=_classify(title),
            budget_max=_parse_inr(budget_raw),
            budget_raw=budget_raw,
            deadline=_parse_date(deadline_raw),
            deadline_raw=deadline_raw,
            published_at=_parse_date(published_raw),
            status=TenderStatus.ACTIVE,
            source_url=source_url,
        )

    def _has_next_page(self, response: httpx.Response, current_page: int) -> bool:
        soup = BeautifulSoup(response.text, "lxml")

        # Look for "Next" pagination link
        next_link = soup.find("a", string=re.compile(r"next|»|>", re.I))
        if next_link:
            return True

        # Look for page numbers — if current page number is not the last one
        page_links = soup.select("a.page-link, .pagination a, td.pagelinks a")
        page_numbers = []
        for link in page_links:
            txt = link.get_text(strip=True)
            if txt.isdigit():
                page_numbers.append(int(txt))

        if page_numbers:
            return current_page < max(page_numbers)

        return False