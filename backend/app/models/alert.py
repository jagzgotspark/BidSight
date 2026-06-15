from sqlalchemy import Column, String, Integer, Boolean, DateTime, func, UniqueConstraint
from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True)          # uuid
    user_id = Column(String, nullable=False, index=True)
    bid_id = Column(String, nullable=False, index=True)
    tender_id = Column(String, nullable=True)
    tender_title = Column(String, default="")
    deadline = Column(DateTime, nullable=True)
    days_left = Column(Integer, nullable=True)
    threshold = Column(Integer, nullable=False)     # bucket that triggered it
    kind = Column(String, default="deadline", server_default="deadline", nullable=False)
    score = Column(Integer, nullable=True)   # the match score, for "match" alerts
    message = Column(String, default="")
    channel = Column(String, default="in_app")
    is_read = Column(Boolean, default=False)
    emailed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    # Prevents duplicate alerts for the same bid at the same threshold
    __table_args__ = (
        UniqueConstraint("bid_id", "threshold", name="uq_alert_bid_threshold"),
    )