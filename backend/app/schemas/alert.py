from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AlertResponse(BaseModel):
    id: str
    bid_id: str
    tender_id: Optional[str]
    tender_title: str
    deadline: Optional[datetime]
    days_left: Optional[int]
    threshold: int
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True