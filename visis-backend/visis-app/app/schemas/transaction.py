# app/schemas/transaction.py

from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

class TransactionInitializeRequest(BaseModel):
    email: EmailStr
    amount: float
    callback_url: Optional[str] = None
    transaction_metadata: Optional[Dict[str, Any]] = None  # Updated field name
    channels: Optional[List[str]] = None
    currency: Optional[str] = "NGN"  # Made optional with default

class TransactionInitializeResponse(BaseModel):
    authorization_url: str
    access_code: str
    reference: str

class TransactionResponse(BaseModel):
    id: int
    reference: str
    amount: float
    currency: str
    status: str
    channel: Optional[str]
    customer_email: EmailStr
    created_at: datetime
    paid_at: Optional[datetime] = None
    authorization_code: Optional[str] = None
    transaction_id: Optional[int] = None
    customer_id: Optional[int] = None
    transaction_metadata: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True

class ChargeAuthorizationRequest(BaseModel):
    email: EmailStr
    amount: float
    authorization_code: str
    reference: Optional[str] = None
    currency: Optional[str] = 'NGN'
    metadata: Optional[Dict[str, Any]] = None

class PartialDebitRequest(BaseModel):
    authorization_code: str
    amount: float
    email: EmailStr
    currency: Optional[str] = 'NGN'
    reference: Optional[str] = None
    at_least: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
