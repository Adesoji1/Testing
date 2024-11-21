

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


from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class UserPreference(Base):
    __tablename__ = 'user_preferences'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    text_to_speech_voice = Column(String, nullable=True)  # Narrator voice preference
    playback_speed = Column(String, nullable=True)  # Audio speed
    audio_format = Column(String, nullable=True, default="MP3")  # Audio format preference
    font_size = Column(String, nullable=True, default="medium")  # Font size for reading
    highlight_color = Column(String, nullable=True, default="yellow")  # Highlight color
    reading_mode = Column(String, nullable=True, default="light")  # Reading mode (light/dark)
    auto_save_bookmark = Column(Boolean, default=True)  # Auto-save bookmarks
    notification_enabled = Column(Boolean, default=True)  # Enable notifications
    default_folder = Column(String, nullable=True, default="My Documents")  # Default folder
    content_visibility = Column(String, nullable=True, default="private")  # Content visibility
    preferred_language = Column(String, nullable=True, default="English")  # Preferred language

    user = relationship("User", back_populates="preferences")
