# app/schemas/donation.py

from pydantic import BaseModel, EmailStr
from typing import Dict, Any

class DonationRequest(BaseModel):
    email: EmailStr
    amount: float  # Amount in Naira

class DonationResponse(BaseModel):
    authorization_url: str
    access_code: str
    reference: str

class PaystackWebhookPayload(BaseModel):
    event: str
    data: Dict[str, Any]
