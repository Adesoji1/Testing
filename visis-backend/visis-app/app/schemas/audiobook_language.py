#app/schemas/audiobook_language.py
from pydantic import BaseModel

class AudioBookLanguageBase(BaseModel):
    audiobook_id: int
    language_id: int

class AudioBookLanguageCreate(AudioBookLanguageBase):
    pass

class AudioBookLanguageResponse(AudioBookLanguageBase):
    id: int

    class Config:
        from_attributes = True