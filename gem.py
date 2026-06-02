from __future__ import annotations

"""
GeM (Government e-Marketplace) Scraper
=======================================
GeM exposes a public search API used by their own portal.
Endpoint: https://bidplus.gem.gov.in/all-bids
API:      https://bidplus.gem.gov.in/bidlists  (JSON, paginated)

This scraper:
  1. Hits the JSON API with page-based pagination.
  2. Normalises each bid into a Tender object.
  3. Falls back to HTML parsing if the JSON API changes shape.

Rate limiting: 2s between pages (GeM's own portal uses the same endpoint).
"""

import re
from datetime import datetime
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from scraper.models.tender import Tender, TenderCategory, TenderSource, TenderStatus
from scraper.scrapers.base import BaseScraper

# Category keyword mapping — quick heuristic before AI classification
_CATEGORY_KEYWORDS: dict[TenderCategory, list[str]] = {
    TenderCategory.IT_SOFTWARE: ["software", "erp", "crm", "mobile app", "web", "portal", "application"],
    TenderCategory.CLOUD: ["cloud", "aws", "azure", "gcp", "saas", "hosting", "server"],
    TenderCategory.AI_ML: ["artificial intelligence", "machine learning", "ai", "ml", "nlp", "data science", "analytics"],
    TenderCategory.CYBERSECURITY: ["cyber", "security", "vapt", "penetration", "firewall", "soc", "siem"],
    TenderCategory.CONSULTING: ["consulting", "advisory", "consultancy", "strategy", "assessment"],
    TenderCategory.INFRASTRUCTURE: ["network", "cabling", "data centre", "datacenter", "hardware", "server", "storage"],
}


def _classify(title: str, description: str = "") -> TenderCategory:
    """Simple keyword-based category classifier. AI pipeline refines this later."""
    text = (title + " " + description).lower()
    for category, keywords in _CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return category
    return TenderCategory.OTHER


def _parse_inr(raw: str) -> Optional[float]:
    """Parse '₹ 1,23,45,678.00' or '1234567' into a float."""
    if not raw:
        return None
    cleaned = re.sub(r"[₹,\s]", "", raw)
    # Handle lakh/crore suffixes
    cleaned_lower = cleaned.lower()
    multiplier = 1.0
    if cleaned_lower.endswith("cr"):
        multiplier = 1_00_00_000
        cleaned = cleaned_lower.replace("cr", "")
    elif cleaned_lower.endswith("l"):
        multiplier = 1_00_000
        cleaned = cleaned_lower.replace("l", "")
    try:
        return float(cleaned) * multiplier
    except ValueError:
        return None


def _parse_date(raw: str) -> Optional[datetime]:
    """Try common GeM date formats."""
    formats = [
        "%d/%m/%Y %I:%M %p",
        "%d/%m/%Y %H:%M",
        "%d-%m-%Y %H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%d %b %Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(raw.strip(), fmt)
        except ValueError:
            continue
    return None


class GeMScraper(BaseScraper):
    """
    Scrapes active bids from GeM's bidplus API.

    The JSON endpoint returns a list of bid objects under `data.bids`.
    Pagination is offset-based via the `page_no` query param.
    """

    source_name = "gem"
    base_url = "https://bidplus.gem.gov.in"
    page_delay_seconds = 2.5

    # GeM API endpoint (public, no auth required)
    _API_URL = "https://bidplus.gem.gov.in/bidlists"

    async def _fetch_listing_page(self, page: int) -> httpx.Response:
        params = {
            "page_no": page,
            "searchedCriteria": "",
        }
        return await self._client.get(self._API_URL, params=params)

    def _parse_listing(self, response: httpx.Response) -> list[Tender]:
        """Parse the JSON API response from GeM."""
        try:
            data = response.json()
        except Exception:
            # Fallback: try HTML parsing if JSON fails
            return self._parse_html_fallback(response.text)

        bids = (
            data.get("data", {}).get("bids", [])
            or data.get("bids", [])
            or []
        )

        tenders: list[Tender] = []
        for bid in bids:
            try:
                tender = self._normalise_bid(bid)
                tenders.append(tender)
            except Exception as exc:
                self.log.warning("bid_parse_error", bid_no=bid.get("bid_no"), error=str(exc))
        return tenders

    def _normalise_bid(self, bid: dict) -> Tender:
        bid_no = str(bid.get("bid_no") or bid.get("bidno") or "")
        title = str(bid.get("bid_title") or bid.get("name") or "").strip()
        authority = str(bid.get("ministry") or bid.get("dept") or "").strip()
        location = str(bid.get("location") or bid.get("state") or "").strip()
        deadline_raw = str(bid.get("bid_end_dt") or bid.get("end_date") or "")
        published_raw = str(bid.get("publish_date") or bid.get("created_on") or "")
        budget_raw = str(bid.get("estimated_value") or bid.get("qty_value") or "")
        description = str(bid.get("item_description") or bid.get("description") or "")
        doc_links = bid.get("documents") or []

        source_url = f"{self.base_url}/viewbid/{bid_no}" if bid_no else ""

        return Tender(
            tender_id=bid_no,
            source=TenderSource.GEM,
            title=title or f"GeM Bid {bid_no}",
            description=description,
            authority=authority,
            location=location,
            category=_classify(title, description),
            budget_max=_parse_inr(budget_raw),
            budget_raw=budget_raw,
            deadline=_parse_date(deadline_raw),
            deadline_raw=deadline_raw,
            published_at=_parse_date(published_raw),
            status=TenderStatus.ACTIVE,
            source_url=source_url,
            document_urls=[d.get("url", "") for d in doc_links if isinstance(d, dict)],
            eligibility_raw=str(bid.get("eligibility") or ""),
        )

    def _parse_html_fallback(self, html: str) -> list[Tender]:
        """
        HTML fallback parser for GeM's /all-bids page.
        Used if the JSON API changes structure.
        """
        soup = BeautifulSoup(html, "lxml")
        tenders: list[Tender] = []

        for row in soup.select(".bid-list-row, tr.bid-row, div.bid-item"):
            try:
                title_el = row.select_one(".bid-title, td.title, .bid-name")
                bid_no_el = row.select_one(".bid-no, td.bid-number")
                deadline_el = row.select_one(".end-date, td.deadline, .closing-date")
                budget_el = row.select_one(".estimated-value, td.value, .bid-value")
                authority_el = row.select_one(".ministry, td.authority, .dept-name")
                link_el = row.select_one("a[href]")

                if not title_el:
                    continue

                title = title_el.get_text(strip=True)
                bid_no = bid_no_el.get_text(strip=True) if bid_no_el else ""
                deadline_raw = deadline_el.get_text(strip=True) if deadline_el else ""
                budget_raw = budget_el.get_text(strip=True) if budget_el else ""
                authority = authority_el.get_text(strip=True) if authority_el else ""
                href = link_el["href"] if link_el else ""
                source_url = href if href.startswith("http") else self.base_url + href

                tenders.append(Tender(
                    tender_id=bid_no or title[:40],
                    source=TenderSource.GEM,
                    title=title,
                    authority=authority,
                    category=_classify(title),
                    budget_max=_parse_inr(budget_raw),
                    budget_raw=budget_raw,
                    deadline=_parse_date(deadline_raw),
                    deadline_raw=deadline_raw,
                    status=TenderStatus.ACTIVE,
                    source_url=source_url,
                ))
            except Exception as exc:
                self.log.warning("html_row_parse_error", error=str(exc))

        return tenders

    def _has_next_page(self, response: httpx.Response, current_page: int) -> bool:
        try:
            data = response.json()
            total = int(data.get("data", {}).get("total_records", 0) or 0)
            per_page = int(data.get("data", {}).get("per_page", 20) or 20)
            return current_page * per_page < total
        except Exception:
            # If we can't parse pagination, stop after the first empty page
            return False