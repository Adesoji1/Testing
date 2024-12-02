# user_bookmark.py (schemas)




# # # user_bookmark.py (schemas)
# #app/schemas/user_bookmark.py
# from pydantic import BaseModel,model_validator, ValidationError
# from typing import List, Optional
# from datetime import datetime

# # Base schema for UserBookmark
# class UserBookmarkBase(BaseModel):
#     document_id: Optional[int] = None
#     audiobook_id: Optional[int] = None
#     position: str
#     timestamp: Optional[str] = None


# # class UserBookmarkCreate(BaseModel):
# #     document_id: Optional[int] = None
# #     audiobook_id: Optional[int] = None
# #     position: str
# #     timestamp: Optional[str] = None
# class UserBookmarkCreate(UserBookmarkBase):
#     @model_validator(mode='after')
#     def check_either_document_or_audiobook(self):
#         if (self.document_id is None) == (self.audiobook_id is None):
#             raise ValueError("Provide either 'document_id' or 'audiobook_id', but not both.")
#         return self
#     model_config = {
#         "from_attributes": True  # Pydantic v2.x
#     }

# # Schema for response
# class UserBookmarkResponse(UserBookmarkBase):
#     id: int
#     user_id: int
#     created_at: datetime  # Ensure this matches your SQLAlchemy model's field name

#     model_config = {
#         "from_attributes": True  # Replaces orm_mode in Pydantic v2.x
#     }

# # Schema for updating a bookmark
# class UserBookmarkUpdate(BaseModel):
#     document_id: Optional[int] = None
#     audiobook_id: Optional[int] = None
#     position: Optional[str] = None
#     timestamp: Optional[str] = None

#     model_config = {
#         "from_attributes": True  # Replaces orm_mode in Pydantic v2.x
#     }

# # Schema for pagination response
# class BookmarkListResponse(BaseModel):
#     total: int
#     skip: int
#     limit: int
#     bookmarks: List[UserBookmarkResponse]

#     model_config = {
#         "from_attributes": True  # Replaces orm_mode in Pydantic v2.x
#     }

# app/schemas/user_bookmark.py
# from pydantic import BaseModel, model_validator
# from datetime import datetime
# from typing import List, Optional

# # Base schema for UserBookmark
# class UserBookmarkBase(BaseModel):
#     document_id: int  # document ID is required
#     title: str  # Title of the document
#     timestamp: str  # The timestamp (e.g., 00:15:30) when the user wants to bookmark
#     audio_url: str


# class UserBookmarkCreate(UserBookmarkBase):
#     @model_validator(mode='after')
#     def check_document_id(self):
#         if not self.document_id:
#             raise ValueError("document_id is required")
#         return self

#     model_config = {
#         "from_attributes": True  # Pydantic v2.x
#     }

# # Schema for response
# class UserBookmarkResponse(UserBookmarkCreate):
#     id: int  # ID for the bookmark entry
#     user_id: int  # User ID associated with the bookmark
#     created_at: datetime  # Created timestamp of the bookmark

#     model_config = {
#         "from_attributes": True  # Pydantic v2.x
#     }

# # Schema for updating a bookmark
# class UserBookmarkUpdate(BaseModel):
#     timestamp: Optional[str] = None  # Timestamp for updating

#     model_config = {
#         "from_attributes": True  # Pydantic v2.x
#     }

# # Schema for pagination response
# class BookmarkListResponse(BaseModel):
#     total: int
#     skip: int
#     limit: int
#     bookmarks: list[UserBookmarkResponse]

#     model_config = {
#         "from_attributes": True  # Pydantic v2.x
#     }


# app/schemas/user_bookmark.py

# from pydantic import BaseModel,Field
# from typing import Optional
# from datetime import datetime

# class UserBookmarkBase(BaseModel):
#     document_id: int
#     title: str
#     timestamp: str  # The timestamp for resume
#     position: Optional[str] = Field(default="00:00:00")

# # For creating a bookmark
# class UserBookmarkCreate(UserBookmarkBase):
#     pass

# class UserBookmarkResponse(UserBookmarkBase):
#     id: int
#     user_id: int
#     audio_url: Optional[str] = None  # audio_url will be fetched based on the document
#     created_at: str  # Assuming datetime string format for created_at

#     class Config:
#         orm_mode = True  # Ensure ORM support by setting from_orm=True
#         # Ensure that datetime fields are formatted properly
#         json_encoders = {
#             datetime: lambda v: v.isoformat()  # Convert datetime to ISO 8601 string format
#         }

# # For updating a bookmark
# class UserBookmarkUpdate(BaseModel):
#     document_id: Optional[int]
#     title: Optional[str]
#     timestamp: Optional[str]

#     class Config:
#         orm_mode = True

# class BookmarkListResponse(BaseModel):
#     total: int
#     skip: int
#     limit: int
#     bookmarks: list[UserBookmarkResponse]  # List of Pydantic model instances

#     class Config:
#         orm_mode = True  # Ensures ORM support for lists


# from pydantic import BaseModel
# from typing import Optional

# class UserBookmarkBase(BaseModel):
#     document_id: int
#     title: str
#     timestamp: str  # The timestamp for resume

# # For creating a bookmark
# class UserBookmarkCreate(UserBookmarkBase):
#     pass

# class UserBookmarkResponse(UserBookmarkBase):
#     id: int
#     user_id: int
#     audio_url: Optional[str] = None  # audio_url will be fetched based on the document
#     created_at: str  # Assuming datetime string format for created_at

# # # For response after creating a bookmark
# # class UserBookmarkResponse(UserBookmarkBase):
# #     id: int
# #     audio_url: str  # This will be dynamically added in the response, no need for it in the request body

#     class Config:
#         orm_mode = True

# # For updating a bookmark
# class UserBookmarkUpdate(BaseModel):
#     document_id: Optional[int]
#     title: Optional[str]
#     timestamp: Optional[str]

#     class Config:
#         orm_mode = True

# class BookmarkListResponse(BaseModel):
#     total: int
#     skip: int
#     limit: int
#     bookmarks: list[UserBookmarkResponse]

#     class Config:
#         orm_mode = True


from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# Base schema for UserBookmark
class UserBookmarkBase(BaseModel):
    document_id: int
    title: Optional[str] = None  # Changed from str to Optional[str]
    timestamp: Optional[str] = None  # Changed from str to Optional[str]
    position: Optional[str] = Field(default="00:00:00")

# class UserBookmarkBase(BaseModel):
#     document_id: int
#     title: str
#     timestamp: str  # The timestamp for resume (stored as VARCHAR in DB)
#     position: Optional[str] = Field(default="00:00:00")
    

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
