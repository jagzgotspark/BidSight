from __future__ import annotations

import abc
import asyncio
from typing import AsyncIterator

import httpx
import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from scraper.models.tender import Tender

logger = structlog.get_logger()

# Shared headers — polite defaults
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/json,*/*;q=0.8",
}


class ScraperError(Exception):
    """Raised when a scraper cannot recover from an error."""


class BaseScraper(abc.ABC):
    """
    Abstract base for all BidSight portal scrapers.

    Subclasses implement:
        _fetch_listing_page(page)  → raw response
        _parse_listing(response)   → list[Tender]
        _has_next_page(response)   → bool

    The public `scrape()` async generator handles:
        - pagination
        - per-request retry with exponential backoff
        - rate-limiting between pages
        - structured logging
    """

    source_name: str = "unknown"
    base_url: str = ""
    page_delay_seconds: float = 2.0      # Be a polite citizen
    max_pages: int = 50                  # Safety ceiling

    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: httpx.AsyncClient | None = None
        self.log = structlog.get_logger(scraper=self.source_name)

    async def __aenter__(self) -> "BaseScraper":
        self._client = httpx.AsyncClient(
            headers=DEFAULT_HEADERS,
            timeout=self.timeout,
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, *_) -> None:
        if self._client:
            await self._client.aclose()

    @abc.abstractmethod
    async def _fetch_listing_page(self, page: int) -> httpx.Response:
        """Fetch a single listing page. Must use self._client."""

    @abc.abstractmethod
    def _parse_listing(self, response: httpx.Response) -> list[Tender]:
        """Parse tenders from a listing response. Must be synchronous."""

    @abc.abstractmethod
    def _has_next_page(self, response: httpx.Response, current_page: int) -> bool:
        """Return True if there is a next page to fetch."""

    async def scrape(self) -> AsyncIterator[Tender]:
        """
        Public entry point. Yields normalised Tender objects one by one.

        Usage:
            async with GeMScraper() as scraper:
                async for tender in scraper.scrape():
                    await save(tender)
        """
        self.log.info("scrape_started")
        total = 0

        for page in range(1, self.max_pages + 1):
            try:
                response = await self._fetch_with_retry(page)
            except ScraperError as exc:
                self.log.error("page_failed", page=page, error=str(exc))
                break

            tenders = self._parse_listing(response)
            self.log.info("page_parsed", page=page, count=len(tenders))

            for tender in tenders:
                total += 1
                yield tender

            if not self._has_next_page(response, page):
                self.log.info("pagination_exhausted", pages=page)
                break

            await asyncio.sleep(self.page_delay_seconds)

        self.log.info("scrape_complete", total_tenders=total)

    async def _fetch_with_retry(self, page: int) -> httpx.Response:
        """Thin retry wrapper around _fetch_listing_page."""
        attempt = 0
        delay = 2.0
        last_exc: Exception | None = None

        while attempt < self.max_retries:
            try:
                response = await self._fetch_listing_page(page)
                response.raise_for_status()
                return response
            except (httpx.HTTPStatusError, httpx.RequestError) as exc:
                attempt += 1
                last_exc = exc
                self.log.warning(
                    "fetch_retry",
                    page=page,
                    attempt=attempt,
                    error=str(exc),
                    next_delay=delay,
                )
                await asyncio.sleep(delay)
                delay = min(delay * 2, 30)

        raise ScraperError(
            f"Failed to fetch page {page} after {self.max_retries} attempts"
        ) from last_exc