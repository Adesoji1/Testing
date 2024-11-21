#models/audiobook.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone

class Audiobook(Base):
    __tablename__ = 'audiobooks'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    narrator = Column(String, nullable=True)
    duration = Column(String, nullable=False)
    genre = Column(String, nullable=True)
    publication_date = Column(DateTime, default=datetime.utcnow)
    file_key = Column(String, nullable=False)
    is_dolby_atmos_supported = Column(Boolean, default=False)
    url = Column(String, nullable=False)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)

    bookmarks = relationship("UserBookmark", back_populates="audiobook", lazy="dynamic")
    document = relationship('Document', back_populates='audiobook')
    # document = relationship("Document", back_populates="audiobook", uselist=False, lazy="joined")

    def __repr__(self):
        return f"<Audiobook(id={self.id}, title={self.title})>"
# app/models/user_bookmark.py

# from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
# from sqlalchemy.orm import relationship
# from app.database import Base
# from datetime import datetime

# class UserBookmark(Base):
#     __tablename__ = 'user_bookmarks'
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
#     document_id = Column(Integer, ForeignKey('documents.id'), nullable=True)
#     audiobook_id = Column(Integer, ForeignKey('audiobooks.id'), nullable=False)
#     note = Column(String,nullable=True)
#     position = Column(String, nullable=False)
#     # date_created = Column(DateTime, default=func.now(), nullable=False)
#     # created_at = Column(DateTime, default=datetime.utcnow)
#     created_at = Column(DateTime, default=func.now(), nullable=False)

#     # Relationships
#     user = relationship("User", back_populates="bookmarks",lazy="joined")
#     audiobook = relationship("Audiobook", back_populates="bookmarks",lazy="joined")
#     document = relationship("Document", back_populates="bookmarks",lazy="joined")