from __future__ import annotations

import hashlib
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_validator, model_validator


class TenderSource(str, Enum):
    GEM = "gem"
    CPPP = "cppp"


class TenderStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


class TenderCategory(str, Enum):
    IT_SOFTWARE = "it_software"
    CLOUD = "cloud"
    AI_ML = "ai_ml"
    CYBERSECURITY = "cybersecurity"
    CONSULTING = "consulting"
    INFRASTRUCTURE = "infrastructure"
    HARDWARE = "hardware"
    OTHER = "other"


class Tender(BaseModel):
    """
    Normalised tender object — every portal scraper must produce this shape.
    The `tender_id` is a stable, portal-scoped identifier (e.g. GeM bid number).
    The `fingerprint` is a content hash used for deduplication.
    """

    # Identity
    tender_id: str                        # Portal's own ID
    source: TenderSource                  # Which portal
    fingerprint: str = ""                 # SHA-256 of (source + tender_id + title)

    # Core fields
    title: str
    description: str = ""
    authority: str = ""                   # Procuring organisation
    location: str = ""                    # State / city
    category: TenderCategory = TenderCategory.OTHER

    # Money
    budget_min: Optional[float] = None    # INR
    budget_max: Optional[float] = None    # INR
    budget_raw: str = ""                  # Original string before parsing

    # Dates
    published_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    deadline_raw: str = ""

    # Status & meta
    status: TenderStatus = TenderStatus.ACTIVE
    source_url: str = ""
    document_urls: list[str] = []
    eligibility_raw: str = ""             # Raw eligibility text for AI processing
    raw_html: str = ""                    # Kept for AI summarisation pipeline

    # Timestamps (set by scraper)
    scraped_at: datetime = datetime.utcnow()

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("title cannot be blank")
        return v

    @model_validator(mode="after")
    def compute_fingerprint(self) -> "Tender":
        if not self.fingerprint:
            raw = f"{self.source.value}:{self.tender_id}:{self.title}"
            self.fingerprint = hashlib.sha256(raw.encode()).hexdigest()
        return self

    @property
    def days_to_deadline(self) -> Optional[int]:
        if self.deadline is None:
            return None
        delta = self.deadline - datetime.utcnow()
        return delta.days

    @property
    def budget_display(self) -> str:
        if self.budget_max:
            cr = self.budget_max / 1_00_00_000
            if cr >= 1:
                return f"₹{cr:.1f} Cr"
            lakh = self.budget_max / 1_00_000
            return f"₹{lakh:.0f}L"
        return self.budget_raw or "N/A"

    def is_duplicate_of(self, other: "Tender") -> bool:
        return self.fingerprint == other.fingerprint