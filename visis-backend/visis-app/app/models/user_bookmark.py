from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class UserBookmark(Base):
    __tablename__ = 'user_bookmarks'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=True)
    audiobook_id = Column(Integer, ForeignKey('audiobooks.id'), nullable=True)
    position = Column(String, nullable=False)
    date_created = Column(DateTime, default=func.now(), nullable=False)

    user = relationship("User", back_populates="bookmarks")
    audiobook = relationship("Audiobook", back_populates="bookmarks")
    document = relationship("Document", back_populates="bookmarks")