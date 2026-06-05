from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from scraper.models.tender import Tender, TenderSource, TenderStatus
from scraper.scrapers.base import BaseScraper
from scraper.scrapers.gem import _classify, _parse_date, _parse_inr

_BASE = "https://eprocure.gov.in"
_LIST_URL = f"{_BASE}/cppp/latestactivetenders"


class CPPPScraper(BaseScraper):
    source_name = "cppp"
    base_url = _BASE
    page_delay_seconds = 3.0
    _LIST_URL = _LIST_URL

    async def _fetch_listing_page(self, page: int) -> httpx.Response:
        params = {"page": page, "sortBy": "publishing_date", "sortOrder": "desc"}
        return await self._client.get(self._LIST_URL, params=params)

    def _parse_listing(self, response: httpx.Response) -> list[Tender]:
        html = response.text
        if "captcha" in html.lower():
            self.log.warning("captcha_detected")
            return []

        soup = BeautifulSoup(html, "lxml")
        tenders: list[Tender] = []
        table = soup.select_one("table#table, table.list_table, table.tablebg")
        if not table:
            return []

        for row in table.select("tr")[1:]:
            try:
                tender = self._parse_row(row)
                if tender:
                    tenders.append(tender)
            except Exception:
                pass
        return tenders

    def _parse_row(self, row) -> Optional[Tender]:
        cells = row.select("td")
        if len(cells) < 4:
            return None

        link_el = row.select_one("a[href]")
        href = link_el["href"] if link_el else ""
        source_url = href if href.startswith("http") else (_BASE + href if href else "")

        tender_id = ""
        id_match = re.search(r"(?:tenderID|tid|ref|id)[=\/]([A-Z0-9\-\/]+)", href, re.I)
        if id_match:
            tender_id = id_match.group(1)

        def cell_text(idx: int) -> str:
            return cells[idx].get_text(strip=True) if idx < len(cells) else ""

        if len(cells) >= 7:
            tender_id = tender_id or cell_text(1)
            title = cell_text(2)
            authority = cell_text(3)
            published_raw = cell_text(4)
            deadline_raw = cell_text(5)
            budget_raw = cell_text(6)
        elif len(cells) >= 5:
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
        next_link = soup.find("a", string=re.compile(r"next|»|>", re.I))
        if next_link:
            return True
        page_links = soup.select("a.page-link, .pagination a, td.pagelinks a")
        page_numbers = []
        for link in page_links:
            txt = link.get_text(strip=True)
            if txt.isdigit():
                page_numbers.append(int(txt))
        if page_numbers:
            return current_page < max(page_numbers)
        return False