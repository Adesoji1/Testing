# app/models/donation.py

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Donation(Base):
    __tablename__ = 'donations'

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String, unique=True, index=True)
    amount = Column(Float)
    email = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="donations")
