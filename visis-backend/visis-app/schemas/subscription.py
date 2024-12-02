# app/schemas/subscription.py

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class SubscriptionRequest(BaseModel):
    email: EmailStr
    plan_code: str

class SubscriptionResponse(BaseModel):
    subscription_id: str
    subscription_code: str
    email_token: str
    plan_code: str
    amount: float
    currency: str
    status: str
    next_payment_date: Optional[datetime]

    class Config:
        orm_mode = True
