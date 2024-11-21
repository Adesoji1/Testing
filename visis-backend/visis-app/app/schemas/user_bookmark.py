# user_bookmark.py (schemas)




# # user_bookmark.py (schemas)
#app/schemas/user_bookmark.py
from pydantic import BaseModel,model_validator, ValidationError
from typing import List, Optional
from datetime import datetime

# Base schema for UserBookmark
class UserBookmarkBase(BaseModel):
    document_id: Optional[int] = None
    audiobook_id: Optional[int] = None
    position: str
    timestamp: Optional[str] = None


# class UserBookmarkCreate(BaseModel):
#     document_id: Optional[int] = None
#     audiobook_id: Optional[int] = None
#     position: str
#     timestamp: Optional[str] = None
class UserBookmarkCreate(UserBookmarkBase):
    @model_validator(mode='after')
    def check_either_document_or_audiobook(self):
        if (self.document_id is None) == (self.audiobook_id is None):
            raise ValueError("Provide either 'document_id' or 'audiobook_id', but not both.")
        return self
    model_config = {
        "from_attributes": True  # Pydantic v2.x
    }

# Schema for response
class UserBookmarkResponse(UserBookmarkBase):
    id: int
    user_id: int
    created_at: datetime  # Ensure this matches your SQLAlchemy model's field name

    model_config = {
        "from_attributes": True  # Replaces orm_mode in Pydantic v2.x
    }

# Schema for updating a bookmark
class UserBookmarkUpdate(BaseModel):
    document_id: Optional[int] = None
    audiobook_id: Optional[int] = None
    position: Optional[str] = None
    timestamp: Optional[str] = None

    model_config = {
        "from_attributes": True  # Replaces orm_mode in Pydantic v2.x
    }

# Schema for pagination response
class BookmarkListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    bookmarks: List[UserBookmarkResponse]

    model_config = {
        "from_attributes": True  # Replaces orm_mode in Pydantic v2.x
    }



