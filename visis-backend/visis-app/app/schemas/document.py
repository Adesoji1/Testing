#app/schemas/document.py
from pydantic import BaseModel, HttpUrl
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
    user_id: int
    upload_date: datetime
    processing_status: str
    processing_error: Optional[str] = None
    file_size: Optional[int] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = []
    audio_url: Optional[str] = None
    detected_language: Optional[str] = None
    genre: Optional[str] = None  # Include the genre field
    audiobook: Optional[AudioBookResponse] = None

    class Config:
        from_attributes = True




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
        from_attributes = True