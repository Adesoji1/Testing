from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime
from pydantic import ConfigDict

class ResolveAccountNumberResponse(BaseModel):
    account_number: str
    account_name: str
    bank_id: int

    model_config = ConfigDict(from_attributes=True)

class ValidateAccountRequest(BaseModel):
    bank_code: str
    country_code: str
    account_number: str
    account_name: str
    account_type: str  # personal or business
    document_type: str  # identityNumber, passportNumber, businessRegistrationNumber
    document_number: str

class ValidateAccountResponse(BaseModel):
    verified: bool
    verificationMessage: str

    model_config = ConfigDict(from_attributes=True)



class Bank(BaseModel):
    name: str
    slug: str
    code: str
    longcode: Optional[str]
    gateway: Optional[str]
    pay_with_bank: bool
    active: bool
    is_deleted: bool
    country: str
    currency: str
    type: str
    id: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        orm_mode = True

class ListBanksResponse(BaseModel):
    status: bool
    message: str
    data: List[Bank]
    meta: Optional[dict] = None

    class Config:
        orm_mode = True