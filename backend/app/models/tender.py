from sqlalchemy import (
    Column, String, Float, DateTime,
    Text, Boolean, func, Index
)
from app.database import Base


class Tender(Base):
    __tablename__ = "tenders"

    # Identity
    id = Column(String, primary_key=True)       # fingerprint (SHA-256)
    tender_id = Column(String, nullable=False)   # portal's own ID
    source = Column(String, nullable=False)      # gem, cppp

    # Core fields
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    authority = Column(String, default="")
    location = Column(String, default="")
    category = Column(String, default="other")

    # Money
    budget_min = Column(Float, nullable=True)
    budget_max = Column(Float, nullable=True)
    budget_raw = Column(String, default="")

    # Dates
    published_at = Column(DateTime, nullable=True)
    deadline = Column(DateTime, nullable=True)
    deadline_raw = Column(String, default="")

    # Status & links
    status = Column(String, default="active")
    source_url = Column(String, default="")
    eligibility_raw = Column(Text, default="")

    # AI fields (populated by Phase 3 AI pipeline)
    ai_summary = Column(Text, nullable=True)
    ai_risk = Column(Text, nullable=True)
    ai_eligibility = Column(Text, nullable=True)
    ai_processed = Column(Boolean, default=False)
    match_score = Column(Float, nullable=True)
    match_reasoning = Column(Text, nullable=True)

    # Timestamps
    scraped_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Indexes for fast querying
    __table_args__ = (
        Index("ix_tenders_source", "source"),
        Index("ix_tenders_deadline", "deadline"),
        Index("ix_tenders_category", "category"),
        Index("ix_tenders_status", "status"),
        Index("ix_tenders_created_at", "created_at"),
    )