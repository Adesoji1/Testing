# app/models/user_preference.py

# from sqlalchemy import Column, Integer, String, ForeignKey
# from sqlalchemy.orm import relationship
# from app.database import Base

# class UserPreference(Base):
#     __tablename__ = 'user_preferences'
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
#     text_to_speech_voice = Column(String)
#     playback_speed = Column(String)
#     preferred_language = Column(String)

#     user = relationship("User", back_populates="preferences")


from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from app.schemas.enums import (
    PlaybackSpeed,
    AudioFormat,
    FontSize,
    HighlightColor,
    ReadingMode,
    ContentVisibility,
    SupportedLanguages
)

class UserPreference(Base):
    __tablename__ = 'user_preferences'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    text_to_speech_voice = Column(String, nullable=True)  # Narrator voice preference
    playback_speed = Column(Enum(PlaybackSpeed), nullable=True, default=PlaybackSpeed.x1_0)  # Audio speed
    audio_format = Column(Enum(AudioFormat), nullable=True, default=AudioFormat.MP3)  # Audio format preference
    font_size = Column(Enum(FontSize), nullable=True, default=FontSize.medium)  # Font size for reading
    highlight_color = Column(Enum(HighlightColor), nullable=True, default=HighlightColor.yellow)  # Highlight color
    reading_mode = Column(Enum(ReadingMode), nullable=True, default=ReadingMode.light)  # Reading mode (light/dark)
    auto_save_bookmark = Column(Boolean, default=True)  # Auto-save bookmarks
    notification_enabled = Column(Boolean, default=True)  # Enable notifications
    default_folder = Column(String, nullable=True, default="My Documents")  # Default folder
    content_visibility = Column(Enum(ContentVisibility), nullable=True, default=ContentVisibility.private)  # Content visibility
    preferred_language = Column(Enum(SupportedLanguages), nullable=True, default=SupportedLanguages.English)  # Preferred language

    user = relationship("User", back_populates="preferences")
