# user_bookmark.py (schemas)

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBookmarkBase(BaseModel):
    document_id: Optional[int] = None
    audiobook_id: Optional[int] = None
    position: str

class UserBookmarkCreate(UserBookmarkBase):
    pass

class UserBookmarkResponse(UserBookmarkBase):
    id: int
    user_id: int
    date_created: datetime

    class Config:
        from_attributes = True