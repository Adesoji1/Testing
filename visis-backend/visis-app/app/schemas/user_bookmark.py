#app/schemas/user_bookmark.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# Base schema for UserBookmark
class UserBookmarkBase(BaseModel):
    document_id: int
    title: Optional[str] = None  # Changed from str to Optional[str]
    timestamp: Optional[str] = None  # Changed from str to Optional[str]
    position: Optional[str] = Field(default="00:00:00")



# For creating a bookmark
class UserBookmarkCreate(UserBookmarkBase):
    pass

# For response
class UserBookmarkResponse(UserBookmarkBase):
    id: int
    user_id: int
    audio_url: Optional[str] = None  # audio_url will be fetched based on the document
    created_at: datetime  # This will be serialized as a string

    class Config:
        from_attributes = True  # Ensures ORM compatibility with SQLAlchemy
        json_encoders = {
            datetime: lambda v: v.isoformat()  # Convert datetime to ISO 8601 string format
        }

# For updating a bookmark
class UserBookmarkUpdate(BaseModel):
    document_id: Optional[int]
    title: Optional[str]
    timestamp: Optional[str]

    class Config:
        from_attributes = True

# Schema for paginated bookmarks
class BookmarkListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    bookmarks: List[UserBookmarkResponse]  # Corrected this to a list of UserBookmarkResponse

    class Config:
        from_attributes = True
