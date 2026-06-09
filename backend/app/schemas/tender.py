from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TenderResponse(BaseModel):
    id: str
    tender_id: str
    source: str
    title: str
    description: str
    authority: str
    location: str
    category: str
    budget_min: Optional[float]
    budget_max: Optional[float]
    budget_raw: str
    published_at: Optional[datetime]
    deadline: Optional[datetime]
    deadline_raw: str
    status: str
    source_url: str
    ai_summary: Optional[str]
    ai_risk: Optional[str]
    ai_eligibility: Optional[str]
    match_score: Optional[float] = None
    match_reasoning: Optional[str] = None
    scraped_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class TenderListResponse(BaseModel):
    items: list[TenderResponse]
    total: int
    page: int
    per_page: int
    pages: int