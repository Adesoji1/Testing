from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from enum import Enum
# from app.schemas.token import TokenData

class SubscriptionType(str, Enum):
    free = "free"
    premium = "premium"


class UserBase(BaseModel):
    username: str
    firstname: str
    lastname: str
    email: EmailStr
    user_type: str

class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserResponse(UserBase):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_admin: bool
    subscription_type: SubscriptionType

    class Config:
        # orm_mode = True
        from_attributes = True

