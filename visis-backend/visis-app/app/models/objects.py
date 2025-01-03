# app/models.py

from sqlalchemy import Column, String, JSON, ARRAY, Text, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
import uuid as UUID, uuid
from datetime import datetime

from app.database import Base

class Document(Base):
    __tablename__ = 'objects'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bucket_id = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    owner = Column(Integer, ForeignKey('users.id'), nullable=False)  # Changed to Integer
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    last_accessed_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    metadata = Column(JSONB, nullable=True)
    path_tokens = Column(ARRAY(Text), nullable=True)
    version = Column(Text, nullable=True)
    user_metadata = Column(JSONB, nullable=True)

    user = relationship("User", back_populates="documents")
