
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Audiobook(Base):
    __tablename__ = 'audiobooks'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    narrator = Column(String, nullable=True)
    duration = Column(String, nullable=True)
    genre = Column(String, nullable=True)
    publication_date = Column(DateTime, nullable=True)
    file_key = Column(String, nullable=True)
    is_dolby_atmos_supported = Column(Boolean, nullable=True)
    url = Column(String, nullable=True)

    bookmarks = relationship("UserBookmark", back_populates="audiobook")

    def __repr__(self):
        return f"<Audiobook(id={self.id}, title={self.title})>"