# models/document.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    file_type = Column(String, nullable=False)
    file_key = Column(String, nullable=False)  # S3 key
    file_size = Column(Integer, nullable=True)  # in bytes
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    url = Column(String, nullable=False)
    
    # Processing related fields
    processing_status = Column(String, default='pending', nullable=False)  # pending, processing, completed, failed
    processing_error = Column(Text, nullable=True)
    audio_url = Column(String, nullable=True)  # URL to processed audio file
    audio_key = Column(String, nullable=True)  # S3 key for audio file
    detected_language = Column(String, nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="documents")
    bookmarks = relationship("UserBookmark", back_populates="document")

    def __repr__(self):
        return f"<Document(id={self.id}, title={self.title}, status={self.processing_status})>"