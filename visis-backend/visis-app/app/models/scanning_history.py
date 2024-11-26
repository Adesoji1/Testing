# app/models/scanning_history.py

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class ScanningHistory(Base):
    __tablename__ = 'scanning_history'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    scan_type = Column(String, nullable=False)
    scan_content = Column(Text, nullable=False)
    scan_date = Column(DateTime, default=datetime.utcnow)
    audio_url = Column(String)  # Add this column
    
    user = relationship("User", back_populates="scanning_history")