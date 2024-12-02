# user_preference.py (schemas)

# from pydantic import BaseModel
# from typing import Optional

# class UserPreferenceBase(BaseModel):
#     text_to_speech_voice: Optional[str]
#     playback_speed: Optional[str]
#     preferred_language: Optional[str]

# class UserPreferenceCreate(UserPreferenceBase):
#     text_to_speech_voice: str
#     playback_speed: str
#     preferred_language: str

# class UserPreferenceUpdate(UserPreferenceBase):
#     pass

# class UserPreferenceResponse(UserPreferenceBase):
#     id: int
#     user_id: int

#     class Config:
#         from_attributes = True

# app/schemas/user_preference.py

# from pydantic import BaseModel, Field
# from typing import Optional
# from app.schemas.enums import SupportedLanguages  # Import the enum

# class UserPreferenceBase(BaseModel):
#     text_to_speech_voice: Optional[str]
#     playback_speed: Optional[str]
#     preferred_language: Optional[SupportedLanguages]  # Use the enum here

# class UserPreferenceCreate(UserPreferenceBase):
#     text_to_speech_voice: str
#     playback_speed: str
#     preferred_language: SupportedLanguages  # Ensure this is required for creation

# class UserPreferenceUpdate(UserPreferenceBase):
#     pass

# class UserPreferenceResponse(UserPreferenceBase):
#     id: int
#     user_id: int

#     class Config:
#         orm_mode = True


# from pydantic import BaseModel, Field
# from typing import Optional
# from app.schemas.enums import SupportedLanguages

# class UserPreferenceBase(BaseModel):
#     text_to_speech_voice: Optional[str] = "default"
#     playback_speed: Optional[str] = "1x"
#     audio_format: Optional[str] = "MP3"
#     font_size: Optional[str] = "medium"
#     highlight_color: Optional[str] = "yellow"
#     reading_mode: Optional[str] = "light"
#     auto_save_bookmark: Optional[bool] = True
#     notification_enabled: Optional[bool] = True
#     default_folder: Optional[str] = "My_Documents"
#     content_visibility: Optional[str] = "private"
#     preferred_language: Optional[SupportedLanguages] = SupportedLanguages.English

# app/schemas/user_preference.py
from pydantic import BaseModel, Field, model_validator
from typing import Optional
from app.schemas.enums import HighlightColor, FontSize, ReadingMode, SupportedLanguages, PlaybackSpeed, AudioFormat, ContentVisibility

class UserPreferenceBase(BaseModel):
    text_to_speech_voice: Optional[str] = "default"
    playback_speed: Optional[PlaybackSpeed] = PlaybackSpeed.x1_0
    audio_format: Optional[AudioFormat] = AudioFormat.MP3
    font_size: Optional[FontSize] = FontSize.medium
    highlight_color: Optional[HighlightColor] = HighlightColor.yellow
    reading_mode: Optional[ReadingMode] = ReadingMode.light
    auto_save_bookmark: Optional[bool] = True
    notification_enabled: Optional[bool] = True
    default_folder: Optional[str] = "My_Documents"
    content_visibility: Optional[ContentVisibility] = ContentVisibility.private
    preferred_language: Optional[SupportedLanguages] = SupportedLanguages.English

    @model_validator(mode="after")
    def validate_voice_and_language(self):
        """Validate that the selected voice matches the preferred language."""
        voice_language_map = {
            "Joanna": "en",
            "Lucia": "es",
            "Celine": "fr",
            "Marlene": "de",
            "Lotte": "nl",
            "Arlet": "ca",
            "Jitka": "cs",
            "Hiujin": "yue",
            "Zhiyu": "cmn",
            "Naja": "da",
            "Suvi": "fi",
            "Isabelle": "fr",
            "Dora": "is",
            "Carla": "it",
            "Tomoko": "ja",
            "Seoyeon": "ko",
            "Liv": "nb",
            "Ola": "pl",
            "Camila": "pt",
            "Carmen": "ro",
            "Tatyana": "ru",
            "Elin": "sv",
            "Filiz": "tr",
            "Gwyneth": "cy-GB",
            "Joanna": "English",
            "Lucia": "Spanish",
            "Celine": "French",
            "Marlene": "German",
            # Add the remaining mappings here
        }
        if self.text_to_speech_voice and self.preferred_language:
            if voice_language_map.get(self.text_to_speech_voice) != self.preferred_language:
                raise ValueError(f"Voice '{self.text_to_speech_voice}' does not match language '{self.preferred_language}'.")
        return self
        # voice = self.text_to_speech_voice
        # language = self.preferred_language
        # # voice = values.get("text_to_speech_voice")
        # # language = values.get("preferred_language")
        # if voice and language:
        #     if voice_language_map.get(voice) != language:
        #         raise ValueError(f"Voice '{voice}' does not match language '{language}'.")
        # return self


class UserPreferenceCreate(UserPreferenceBase):
    text_to_speech_voice: str
    playback_speed: PlaybackSpeed
    audio_format: AudioFormat
    preferred_language: SupportedLanguages

class UserPreferenceUpdate(UserPreferenceBase):
    pass

class UserPreferenceResponse(UserPreferenceBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
