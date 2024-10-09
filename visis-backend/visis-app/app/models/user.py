from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    user_type = Column(String, default="user", nullable=True)
    registration_date = Column(DateTime, default=datetime.utcnow)
    last_login_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    preferences = relationship("UserPreference", back_populates="user")
    documents = relationship("Document", back_populates="user")
    bookmarks = relationship("UserBookmark", back_populates="user")
    scanning_history = relationship("ScanningHistory", back_populates="user")
    accessibility = relationship("Accessibility", back_populates="user")
    activities = relationship("UserActivity", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")