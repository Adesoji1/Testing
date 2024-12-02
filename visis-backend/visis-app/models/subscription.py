# app/models/subscription.py

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(String, unique=True, index=True)
    subscription_code = Column(String, unique=True, index=True)
    email_token = Column(String)
    plan_code = Column(String)
    amount = Column(Float)
    currency = Column(String)
    status = Column(String)
    next_payment_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="subscriptions")
