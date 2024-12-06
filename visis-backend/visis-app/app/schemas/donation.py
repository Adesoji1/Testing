# app/schemas/donation.py

# from pydantic import BaseModel, EmailStr
# from typing import Dict, Any

# class DonationRequest(BaseModel):
#     email: EmailStr
#     amount: float  # Amount in Naira

# class DonationResponse(BaseModel):
#     authorization_url: str
#     access_code: str
#     reference: str

# class PaystackWebhookPayload(BaseModel):
#     event: str
#     data: Dict[str, Any]


# app/schemas/donation.py

# from pydantic import BaseModel, EmailStr, Field
# from typing import Optional, Dict, Any
# from datetime import datetime

# class DonationInitializeRequest(BaseModel):
#     email: EmailStr
#     amount: float  # In Naira
#     channel: str = Field(default="card", description="Payment channel (e.g., card, bank_transfer, ussd, mobile_money, qr, opay)")
#     # Additional fields based on channel
#     bank_code: Optional[str] = None
#     account_number: Optional[str] = None
#     ussd_type: Optional[str] = None
#     mobile_money_provider: Optional[str] = None
#     qr_provider: Optional[str] = None
#     opay_account_number: Optional[str] = None
#     metadata: Optional[Dict[str, Any]] = None

# class DonationInitializeResponse(BaseModel):
#     authorization_url: str
#     access_code: str
#     reference: str

# class DonationResponse(BaseModel):
#     donation_id: Optional[int] = None
#     reference: str
#     amount: float
#     currency: str
#     status: str
#     paid_at: Optional[datetime] = None
#     channel: Optional[str] = None
#     customer_email: EmailStr
#     authorization_code: Optional[str] = None
#     metadata: Optional[Dict[str, Any]] = None

#     class Config:
#         orm_mode = True


# app/schemas/donation.py

# app/schemas/donation.py

# app/schemas/donation.py

from typing import Optional, Dict, Any,Union
from pydantic import BaseModel, EmailStr, Field, model_validator, field_validator
from datetime import datetime
import json

class DonationInitializeRequest(BaseModel):
    email: EmailStr
    first_name: str = Field(..., max_length=100, description="Donor's first name")
    last_name: str = Field(..., max_length=100, description="Donor's last name")
    amount: float = Field(..., gt=0, description="Amount must be greater than zero")
    channel: str = Field(..., description="Payment channel: 'card', 'bank', 'ussd', 'mobile_money', 'qr', 'opay'")
    
    # Optional fields for specific channels
    bank_code: Optional[str] = Field(None, description="Bank code for bank transfers")
    account_number: Optional[str] = Field(None, description="Account number for bank transfers")
    ussd_type: Optional[str] = Field(None, description="USSD type for mobile payments")
    mobile_money_provider: Optional[str] = Field(None, description="Mobile money provider")
    qr_provider: Optional[str] = Field(None, description="QR code provider")
    opay_account_number: Optional[str] = Field(None, description="OPay account number")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
  

    @model_validator(mode='after')
    def validate_channel_fields(cls, values):
        channel = values.channel  # Direct attribute access
        if channel == 'card':
            if not values.bank_code or not values.account_number:
                raise ValueError("bank_code and account_number are required for card payments.")
        elif channel == 'bank':
            if not values.bank_code or not values.account_number:
                raise ValueError("bank_code and account_number are required for bank transfers.")
        elif channel == 'ussd':
            if not values.ussd_type:
                raise ValueError("ussd_type is required for USSD payments.")
        elif channel == 'mobile_money':
            if not values.mobile_money_provider:
                raise ValueError("mobile_money_provider is required for mobile money payments.")
        elif channel == 'qr':
            if not values.qr_provider:
                raise ValueError("qr_provider is required for QR payments.")
        elif channel == 'opay':
            if not values.opay_account_number:
                raise ValueError("opay_account_number is required for OPAY payments.")
        else:
            raise ValueError(f"Unsupported payment channel: {channel}")
        return values

class DonationInitializeResponse(BaseModel):
    authorization_url: str
    access_code: str
    reference: str

class DonationResponse(BaseModel):
    donation_id: Optional[int] = None
    reference: str
    amount: float
    currency: str
    status: str
    paid_at: Optional[datetime] = None
    channel: Optional[str] = None
    customer_email: EmailStr
    authorization_code: Optional[str] = None
    donation_metadata: Optional[Union[Dict[str, Any], str]] = None
    # donation_metadata: Optional[Dict[str, Any]] = None
    first_name: str
    last_name: str

    @field_validator('donation_metadata')
    def parse_metadata(cls, value):
        if isinstance(value, str) and value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                raise ValueError('donation_metadata is not valid JSON')
        return value

    class Config:
        orm_mode = True

