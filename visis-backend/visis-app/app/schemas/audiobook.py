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
     
    class Config:
        orm_mode = True

class AudioBookCreate(BaseModel):
    title: str
    author: str
    narrator: str # Default value
    duration: str  # Default value
    genre: str  # Default value
    publication_date: datetime
    file_key: str
    url: str
    is_dolby_atmos_supported: bool
    document_id : int


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
    document_id: Optional[int] = None 

class AudioBookResponse(BaseModel):
    id: int
    title: str
    narrator: str
    duration: str
    genre: str
    publication_date: datetime
    author: str
    url: str
    is_dolby_atmos_supported: bool
    document_id: int
    

    class Config:
        orm_mode = True

    # model_config = {
    #     "from_attributes": True  # Pydantic v2.x configuration
    # }

