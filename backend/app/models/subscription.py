from sqlalchemy import Column, String, Integer, DateTime, func
from app.database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    plan = Column(String, nullable=False, default="professional")
    status = Column(String, nullable=False, default="created")  # created, active, expired, cancelled
    amount_paise = Column(Integer, nullable=False)
    razorpay_order_id = Column(String, nullable=True, index=True)
    razorpay_payment_id = Column(String, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
