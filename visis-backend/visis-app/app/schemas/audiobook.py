from pydantic import BaseModel
from datetime import datetime

class AudioBookBase(BaseModel):
    title: str
    author: str
    narrator: str
    duration: str
    genre: str
    publication_date: datetime
    file_path: str
    is_dolby_atmos_supported: bool
    url: str

class AudioBookCreate(AudioBookBase):
    pass

class AudioBookResponse(AudioBookBase):
    id: int

    class Config:
        from_attributes = True