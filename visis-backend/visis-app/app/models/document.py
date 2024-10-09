from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String)
    author = Column(String)
    file_type = Column(String)
    file_path = Column(String)
    upload_date = Column(DateTime)
    is_public = Column(Boolean)
    url = Column(String, nullable=False)

    user = relationship("User", back_populates="documents")