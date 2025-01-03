

#app/models/document.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.database import Base

class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_key = Column(String, nullable=False)
    is_public = Column(Boolean, default=False)
    url = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    processing_status = Column(String, default='pending')
    processing_error = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    description = Column(String, nullable=True)
    tags = Column(JSONB, nullable=True)
    # tags = Column(JSON, nullable=True)  # Store tags as JSON (list of strings)
    audio_url = Column(String, nullable=True)
    audio_key = Column(String, nullable=True)
    detected_language = Column(String, nullable=True)
    genre = Column(String, nullable=True)  # Add the genre field
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    play_count = Column(Integer, default=0, nullable=False) # Add play_count field

    # Relationship with Audiobook
    user = relationship('User', back_populates='documents')
    audiobook = relationship("Audiobook", back_populates="document", uselist=False)
    bookmarks = relationship('UserBookmark', back_populates='document')
