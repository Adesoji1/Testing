# app/models/donation.py

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Donation(Base):
    __tablename__ = "donations"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(50), unique=True, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="NGN")
    status = Column(String(20), nullable=False, default="initialized")
    paid_at = Column(DateTime(timezone=True), nullable=True)
    channel = Column(String(50), nullable=False, default="card")
    customer_email = Column(String(255), nullable=False)
    authorization_code = Column(String(255), nullable=True)
    donation_metadata = Column(JSON, nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    user = relationship("User", back_populates="donations")
