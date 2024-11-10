# schemas/audiobook.py
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class AudioBookBase(BaseModel):
    title: str
    author: str
    narrator: str
    duration: str
    genre: str
    publication_date: datetime
    file_key: str  # Use file_key instead of file_path
    is_dolby_atmos_supported: bool
    url: str

class AudioBookCreate(AudioBookBase):
    pass

class AudioBookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    narrator: Optional[str] = None
    duration: Optional[str] = None
    genre: Optional[str] = None
    publication_date: Optional[datetime] = None
    file_key: Optional[str] = None  # Use file_key instead of file_path
    is_dolby_atmos_supported: Optional[bool] = None
    url: Optional[str] = None

class AudioBookResponse(AudioBookBase):
    id: int

    class Config:
        orm_mode = True