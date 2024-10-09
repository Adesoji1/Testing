from sqlalchemy import Column, Integer, ForeignKey
from app.database import Base

class DocumentLanguage(Base):
    __tablename__ = 'document_languages'
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id'))
    language_id = Column(Integer, ForeignKey('languages.id'))