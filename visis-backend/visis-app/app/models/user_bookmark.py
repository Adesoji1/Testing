from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class UserBookmark(Base):
    __tablename__ = 'user_bookmarks'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=True)
    audiobook_id = Column(Integer, ForeignKey('audiobooks.id'), nullable=True)
    position = Column(String)
    date_created = Column(DateTime)

    user = relationship("User", back_populates="bookmarks")