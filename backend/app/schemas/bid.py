from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class BidCreate(BaseModel):
    tender_id: str
    stage: str = "new"
    notes: str = ""


class BidUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stage: Optional[str] = None
    notes: Optional[str] = None
    match_score: Optional[float] = None


class BidResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    tender_id: str
    stage: str
    match_score: Optional[float] = None
    notes: str
    created_at: datetime
    updated_at: datetime

    # Tender details (joined)
    tender_title: Optional[str] = None
    tender_authority: Optional[str] = None
    tender_deadline: Optional[datetime] = None
    tender_budget_raw: Optional[str] = None
    tender_source: Optional[str] = None
