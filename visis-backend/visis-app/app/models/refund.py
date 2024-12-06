# app/models/refund.py

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Refund(Base):
    __tablename__ = "refunds"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String, unique=True, index=True, nullable=False)
    transaction_reference = Column(String, nullable=False)
    amount = Column(Float, nullable=False)  # Stored in Naira
    currency = Column(String, default="NGN", nullable=False)
    status = Column(String, default="pending", nullable=False)
    processor = Column(String, nullable=True)
    refund_metadata = Column(JSON, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"),nullable=False)
    user = relationship("User", back_populates="refunds")
