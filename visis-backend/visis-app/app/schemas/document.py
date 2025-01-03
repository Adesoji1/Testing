#app/schemas/document.py
from pydantic import BaseModel, HttpUrl,validator
from datetime import datetime
from typing import Optional, List
from app.schemas.audiobook import AudioBookResponse

class DocumentBase(BaseModel):
    title: str
    author: str
    file_type: str
    file_key: str  # Use file_key instead of file_path
    is_public: bool = False
    url: str
    created_at: Optional[datetime] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = []
    detected_language: Optional[str] = None
    genre: Optional[str] = None  # Include the genre field
    processing_status: Optional[str] = "pending"
    processing_error: Optional[str] = None

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    is_public: Optional[bool] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None

class DocumentResponse(DocumentBase):
    id: int
    is_public: bool
    file_type: str
    file_key: str
    user_id: int
    upload_date: datetime
    processing_status: str
    processing_error: Optional[str] = None
    file_size: Optional[int] = None
    description: Optional[str] = None
    author: str
    # tags: Optional[List[str]] = []
    audio_url: Optional[str] = None
    detected_language: Optional[str] = None
    genre: Optional[str] = None  # Include the genre field
    audiobook: Optional[AudioBookResponse] = None
    created_at: datetime

    @validator('tags', pre=True, always=True)
    def split_tags(cls, v):
        if isinstance(v, str):
            # Split the string by commas and strip whitespace
            return [tag.strip() for tag in v.split(',')]
        elif isinstance(v, list):
            return v
        return []

    class Config:
        orm_mode = True
        #from_attributes = True
        




class DocumentFilter(BaseModel):
    search: Optional[str] = None
    status: Optional[str] = None
    file_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

# Document Stats
class DocumentStats(BaseModel):
    total_documents: int
    processed_documents: int
    failed_documents: int
    total_storage_used: float  # In MB

    class Config:
        orm_mode = True
        #from_attributes = True
       