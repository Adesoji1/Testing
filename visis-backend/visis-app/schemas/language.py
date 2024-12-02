# app/schemas/language.py

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

class VoiceDetails(BaseModel):
    id: str
    name: str
    gender: str
    language_code: str
    engine: Optional[str] = None
    supported_features: Optional[List[str]] = None

class LanguageBase(BaseModel):
    name: str = Field(..., example="English")
    code: str = Field(..., example="en-US", description="ISO language code")
    display_name: Optional[str] = Field(None, example="English (United States)")
    is_active: bool = Field(default=True)
    native_name: Optional[str] = Field(None, example="English")

class LanguageCreate(LanguageBase):
    pass

class LanguageUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    display_name: Optional[str] = None
    is_active: Optional[bool] = None
    native_name: Optional[str] = None

class PopularLanguage(BaseModel):
    code: str
    name: str
    usage_count: int
    last_used: datetime

class LanguageStats(BaseModel):
    total_languages: int
    active_languages: int
    total_voices: int
    language_usage: Dict[str, int]
    popular_languages: List[PopularLanguage]
    last_updated: datetime

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }

class DetectLanguageResponse(BaseModel):
    detected_language: str = Field(..., example="en-US")
    confidence: float = Field(..., ge=0, le=1, example=0.95)
    alternative_languages: List[Dict[str, float]] = Field(
        default=[],
        description="List of alternative language detections with confidence scores"
    )
    suggested_voices: List[VoiceDetails] = []

class LanguageResponse(LanguageBase):
    id: int
    voices: List[VoiceDetails] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    usage_count: Optional[int] = Field(0, description="Number of times language has been used")

    model_config = {
        "from_attributes": True
    }

class LanguagePreference(BaseModel):
    primary_language: str = Field(..., example="en-US")
    secondary_languages: List[str] = Field(default=[], max_items=5)
    preferred_voice: Optional[str] = None
    auto_detect: bool = Field(default=True)
    fallback_language: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


