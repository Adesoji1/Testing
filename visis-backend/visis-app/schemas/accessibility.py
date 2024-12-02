from pydantic import BaseModel

class AccessibilityBase(BaseModel):
    screen_reader_enabled: bool
    voice_commands_enabled: bool
    text_highlighting_enabled: bool

class AccessibilityCreate(AccessibilityBase):
    pass

class AccessibilityResponse(AccessibilityBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True