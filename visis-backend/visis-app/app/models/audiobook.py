from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.database import Base

class AudioBook(Base):
    __tablename__ = 'audiobooks'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
    narrator = Column(String)
    duration = Column(String)
    genre = Column(String)
    publication_date = Column(DateTime)
    file_path = Column(String)
    is_dolby_atmos_supported = Column(Boolean)
    url = Column(String, nullable=False)
