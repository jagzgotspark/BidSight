from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PlanOut(BaseModel):
    id: str
    name: str
    amount_paise: int
    amount_display: str
    interval_days: int
    features: list[str]


class CheckoutRequest(BaseModel):
    plan: str = "professional"


class CheckoutResponse(BaseModel):
    order_id: str
    amount_paise: int
    currency: str = "INR"
    razorpay_key_id: str
    plan: str


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class SubscriptionStatus(BaseModel):
    plan: str
    status: str
    current_period_end: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True
