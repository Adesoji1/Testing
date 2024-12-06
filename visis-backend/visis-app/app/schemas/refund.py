# app/schemas/refund.py

from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime

class RefundCreateRequest(BaseModel):
    transaction_reference: str
    amount: Optional[float] = None  # In Naira for partial refunds
    metadata: Optional[Dict[str, Any]] = None

class RefundResponse(BaseModel):
    refund_id: Optional[int] = None
    reference: str
    transaction_reference: str
    amount: float
    currency: str
    status: str
    processor: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
