from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
# from app.schemas.token import TokenData


# class TokenData(BaseModel):
#     username: str | None = None  # Changed from user_id to username

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

    class Config:
        # orm_mode = True
        from_attributes = True
