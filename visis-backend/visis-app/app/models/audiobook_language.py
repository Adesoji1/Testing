from sqlalchemy import Column, Integer, ForeignKey
from app.database import Base

class AudioBookLanguage(Base):
    __tablename__ = 'audiobook_languages'
    id = Column(Integer, primary_key=True, index=True)
    audiobook_id = Column(Integer, ForeignKey('audiobooks.id'))
    language_id = Column(Integer, ForeignKey('languages.id'))