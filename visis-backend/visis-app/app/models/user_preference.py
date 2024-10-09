from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class UserPreference(Base):
    __tablename__ = 'user_preferences'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    text_to_speech_voice = Column(String)
    playback_speed = Column(String)
    preferred_language = Column(String)

    user = relationship("User", back_populates="preferences")