# app/models/language.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Language(Base):
    __tablename__ = 'languages'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False, unique=True)
    display_name = Column(String, nullable=True)  # Made nullable
    is_active = Column(Boolean, default=True, nullable=False)
    native_name = Column(String, nullable=True)  # Made nullable
    usage_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, nullable=True)
