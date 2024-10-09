from pydantic import BaseModel
from datetime import datetime

class UserBookmarkBase(BaseModel):
    document_id: int | None
    audiobook_id: int | None
    position: str
    date_created: datetime

class UserBookmarkCreate(UserBookmarkBase):
    pass

class UserBookmarkResponse(UserBookmarkBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True