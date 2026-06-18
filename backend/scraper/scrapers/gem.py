from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from scraper.models.tender import Tender, TenderCategory, TenderSource, TenderStatus
from scraper.scrapers.base import BaseScraper

_CATEGORY_KEYWORDS: dict[TenderCategory, list[str]] = {
    # IT-related — checked first since "security" etc. could clash with physical security services
    TenderCategory.IT_SOFTWARE: ["software", "erp", "mobile app", "web", "portal", "application", "crm"],
    TenderCategory.CLOUD: ["cloud", "aws", "azure", "saas", "hosting", "data center service"],
    TenderCategory.AI_ML: ["artificial intelligence", "machine learning", " ai ", "ml model", "data science", "analytics platform"],
    TenderCategory.CYBERSECURITY: ["cyber security", "vapt", "penetration test", "firewall", "soc service"],
    TenderCategory.CONSULTING: ["consulting", "advisory", "consultancy", "assessment study"],
    TenderCategory.INFRASTRUCTURE: ["network", "cabling", "datacenter", "data centre", "it storage"],
    TenderCategory.HARDWARE: ["laptop", "desktop", "computer", "printer", "server hardware", "ups", "projector"],

    # Non-IT — the bulk of real GeM volume
    TenderCategory.MEDICAL: ["medical", "hospital", "surgical", "pharma", "drug", "tab.", "syringe", "catheter", "diagnostic", "x-ray", "ventilator", "ambulance", "laryngoscope", "endoscop", "laparoscop", "airway scope", "nerve monitoring", "elispot", "antibiotic", "biochemistry", "microbiology", "mr imaging", "gamma knife", "aiims", "clinical", "operative", "patient", "icu", "dialysis", "oxygen concentrator", "defibrillator"],
    TenderCategory.CONSTRUCTION: ["construction", "civil work", "building work", "renovation", "road work", "infrastructure work", "tender for construction"],
    TenderCategory.EQUIPMENT_MACHINERY: ["earth moving", "excavator", "dumper", "tractor", "crane", "generator", "compressor", "machine", "machinery", "equipment hire"],
    TenderCategory.VEHICLES: ["vehicle", "bus", "car", "ambulance", "two wheeler", "motor cycle", "tipper"],
    TenderCategory.FURNITURE: ["furniture", "chair", "table", "almirah", "cabinet", "desk", "sofa"],
    TenderCategory.ELECTRICAL: ["electrical", "wiring", "transformer", "switchgear", "cable", "led light", "solar panel"],
    TenderCategory.TEXTILES_APPAREL: ["uniform", "textile", "fabric", "garment", "apparel", "shoes", "footwear"],
    TenderCategory.FOOD_CATERING: ["catering", "food supply", "ration", "canteen", "meal"],
    TenderCategory.OFFICE_SUPPLIES: ["stationery", "paper", "printing service", "office supply"],
    TenderCategory.SECURITY_SERVICES: ["security guard", "security service", "manpower security", "watchman"],
    TenderCategory.MAINTENANCE_AMC: ["amc", "annual maintenance", "cmc", "housekeeping", "facility management", "repair and overhauling", "repair, maintenance", "overhaul"],
    TenderCategory.INDUSTRIAL_PARTS: ["bearing", "valve", "gasket", "shelving rack", "ballast block", "union 1/2", "spare part", "industrial component", "vacuum cleaner", "cylinder", "skid steer"],
    TenderCategory.DEFENSE_MARINE: ["submarine", "naval", "marine unit", "battery type", "tps", "ugssn", "kpcl", "defence", "armed forces"],
    TenderCategory.LIBRARY_PUBLISHING: ["database subscription", "library", "journal", "publication", "signage"],
}
}


def _classify(title: str, description: str = "") -> TenderCategory:
    text = (title + " " + description).lower()
    for category, keywords in _CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return category
    return TenderCategory.OTHER


def _parse_inr(raw: str) -> Optional[float]:
    if not raw:
        return None
    cleaned = re.sub(r"[₹,\s]", "", str(raw))
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
    formats = [
        "%d/%m/%Y %I:%M %p",
        "%d/%m/%Y %H:%M",
        "%d-%m-%Y %H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%d %b %Y",
        "%Y-%m-%d %H:%M:%S",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(str(raw).strip(), fmt)
        except ValueError:
            continue
    return None


class GeMScraper(BaseScraper):
    """
    Scrapes GeM using the internal /all-bids-data JSON API.
    Discovered by intercepting XHR calls from the browser.
    """
    source_name = "gem"
    base_url = "https://bidplus.gem.gov.in"
    page_delay_seconds = 2.0

    # The real data endpoint — returns JSON directly
    _API_URL = "https://bidplus.gem.gov.in/all-bids-data"
    _PAGE_SIZE = 20

    async def _fetch_listing_page(self, page: int) -> httpx.Response:
        params = {
            "page_no": page,
            "rows": self._PAGE_SIZE,
            "searchedCriteria": "",
            "byType": "all",
            "sort": "Bid-End-Date-Oldest",
        }
        # Use browser-like headers so the API doesn't block us
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Referer": "https://bidplus.gem.gov.in/all-bids",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
        }
        return await self._client.get(self._API_URL, params=params, headers=headers)

    def _parse_listing(self, response: httpx.Response) -> list[Tender]:
        try:
            data = response.json()
        except Exception as exc:
            self.log.warning("json_parse_error", error=str(exc))
            return []

        # Navigate the response structure
        docs = (
            data.get("response", {})
                .get("response", {})
                .get("docs", [])
            or data.get("docs", [])
            or []
        )

        tenders: list[Tender] = []
        for doc in docs:
            try:
                tenders.append(self._normalise_doc(doc))
            except Exception as exc:
                self.log.warning("doc_parse_error", error=str(exc))
        return tenders

    def _normalise_doc(self, doc: dict) -> Tender:
        def first(val):
            """GeM wraps most values in lists."""
            if isinstance(val, list):
                return val[0] if val else ""
            return val or ""

        bid_id = str(first(doc.get("id") or doc.get("b_id", "")))
        bid_number = str(first(doc.get("b_bid_number", "")))
        title = str(first(doc.get("b_category_name") or doc.get("b_title", ""))).strip()
        authority = str(first(doc.get("b_ministry_name") or doc.get("b_dept_name", ""))).strip()
        location = str(first(doc.get("b_state", ""))).strip()
        deadline_raw = str(first(doc.get("b_bid_end_date") or doc.get("b_end_date", "")))
        published_raw = str(first(doc.get("b_publish_date") or doc.get("b_start_date", "")))
        budget_raw = str(first(doc.get("b_estimated_amount") or doc.get("b_total_value", "")))

        source_url = f"{self.base_url}/viewbid/{bid_number}" if bid_number else ""

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

    def _has_next_page(self, response: httpx.Response, current_page: int) -> bool:
        try:
            data = response.json()
            num_found = (
                data.get("response", {})
                    .get("response", {})
                    .get("numFound", 0)
                or 0
            )
            return current_page * self._PAGE_SIZE < int(num_found)
        except Exception:
            return False