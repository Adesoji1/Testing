# app/models/user_bookmark.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class UserBookmark(Base):
    __tablename__ = 'user_bookmarks'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=True)
    audiobook_id = Column(Integer, ForeignKey('audiobooks.id'), nullable=False)
    position = Column(String, nullable=False)
    timestamp = Column(String, nullable=True)  # Optional, for storing audiobook timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    title = Column(String)

    # Relationships
    user = relationship("User", back_populates="bookmarks",lazy="joined")
    audiobook = relationship("Audiobook", back_populates="bookmarks",lazy="joined")
    document = relationship("Document", back_populates="bookmarks",lazy="joined")