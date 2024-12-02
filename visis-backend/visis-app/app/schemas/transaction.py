# app/schemas/transaction.py

# from pydantic import BaseModel, EmailStr
# from typing import Optional
# from datetime import datetime

# class TransactionRequest(BaseModel):
#     email: EmailStr
#     amount: float  # Amount in Naira

# class TransactionResponse(BaseModel):
#     transaction_id: str
#     reference: str
#     amount: float
#     currency: str
#     status: str
#     paid_at: Optional[datetime]
#     channel: Optional[str]
#     customer_email: str
#     authorization_code: Optional[str]

#     class Config:
#         orm_mode = True

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class TransactionRequest(BaseModel):
    email: EmailStr
    amount: float  # Amount in Naira

class TransactionResponse(BaseModel):
    transaction_id: Optional[str] = None  # Made optional
    reference: str
    amount: float
    currency: str
    status: str
    paid_at: Optional[datetime] = None
    channel: Optional[str] = None
    customer_email: str
    authorization_code: Optional[str] = None

    class Config:
        orm_mode = True

class TransactionInitializeResponse(BaseModel):
    authorization_url: str
    access_code: str
    reference: str





