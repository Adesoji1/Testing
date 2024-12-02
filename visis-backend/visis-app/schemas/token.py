from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None
    user_type: str
    firstname: str
    lastname: str

class TokenData(BaseModel):
    username: str | None = None