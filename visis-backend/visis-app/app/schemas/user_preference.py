from pydantic import BaseModel

class UserPreferenceBase(BaseModel):
    text_to_speech_voice: str
    playback_speed: str
    preferred_language: str

class UserPreferenceCreate(UserPreferenceBase):
    pass

class UserPreferenceResponse(UserPreferenceBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True