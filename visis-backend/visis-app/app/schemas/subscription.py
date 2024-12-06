# app/schemas/subscription.py

# from pydantic import BaseModel, EmailStr
# from typing import Optional
# from datetime import datetime

# class SubscriptionRequest(BaseModel):
#     email: EmailStr
#     plan_code: str

# class SubscriptionResponse(BaseModel):
#     subscription_id: str
#     subscription_code: str
#     email_token: str
#     plan_code: str
#     amount: float
#     currency: str
#     status: str
#     next_payment_date: Optional[datetime]

#     class Config:
#         orm_mode = True


# app/schemas/subscription.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime

class SubscriptionInitializeRequest(BaseModel):
    email: EmailStr
    amount: float  # In Naira
    plan_code: str
    channel: str = Field(default="card", description="Payment channel (e.g., card, bank_transfer, ussd, mobile_money, qr, opay)")
    # Additional fields based on channel
    bank_code: Optional[str] = None
    account_number: Optional[str] = None
    ussd_type: Optional[str] = None
    mobile_money_provider: Optional[str] = None
    qr_provider: Optional[str] = None
    opay_account_number: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class SubscriptionInitializeResponse(BaseModel):
    authorization_url: str
    access_code: str
    reference: str

class SubscriptionResponse(BaseModel):
    subscription_id: Optional[int] = None
    reference: str
    plan_code: str
    amount: float
    currency: str
    status: str
    start_date: datetime
    next_payment_date: Optional[datetime] = None
    channel: Optional[str] = None
    customer_email: EmailStr
    subscription_metadata: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True

