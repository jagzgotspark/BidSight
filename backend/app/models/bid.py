from sqlalchemy import Column, String, Float, Text, DateTime, ForeignKey, func
from app.database import Base


class Bid(Base):
    __tablename__ = "bids"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    tender_id = Column(String, ForeignKey("tenders.id"), nullable=False)

    # Pipeline stage
    stage = Column(String, default="new")
    # new → interested → evaluating → drafting → submitted → won → lost

    # Match score (set by matching engine)
    match_score = Column(Float, nullable=True)

    # Notes
    notes = Column(Text, default="")

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())