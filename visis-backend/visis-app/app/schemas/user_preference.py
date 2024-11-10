# user_preference.py (schemas)

from pydantic import BaseModel
from typing import Optional

class UserPreferenceBase(BaseModel):
    text_to_speech_voice: Optional[str]
    playback_speed: Optional[str]
    preferred_language: Optional[str]

class UserPreferenceCreate(UserPreferenceBase):
    text_to_speech_voice: str
    playback_speed: str
    preferred_language: str

class UserPreferenceUpdate(UserPreferenceBase):
    pass

class UserPreferenceResponse(UserPreferenceBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True