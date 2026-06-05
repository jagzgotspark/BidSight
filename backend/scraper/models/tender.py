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
    tender_id: str
    source: TenderSource
    fingerprint: str = ""
    title: str
    description: str = ""
    authority: str = ""
    location: str = ""
    category: TenderCategory = TenderCategory.OTHER
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    budget_raw: str = ""
    published_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    deadline_raw: str = ""
    status: TenderStatus = TenderStatus.ACTIVE
    source_url: str = ""
    document_urls: list[str] = []
    eligibility_raw: str = ""
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
    def budget_display(self) -> str:
        if self.budget_max:
            cr = self.budget_max / 1_00_00_000
            if cr >= 1:
                return f"₹{cr:.1f} Cr"
            lakh = self.budget_max / 1_00_000
            return f"₹{lakh:.0f}L"
        return self.budget_raw or "N/A"