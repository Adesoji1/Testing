# app/models/user.py

from sqlalchemy import Column, Integer, String, DateTime,Boolean, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
from enum import Enum 

class SubscriptionType(str, Enum):
    free = "free"
    premium = "premium"

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    user_type = Column(String, default="user", nullable=True)
    registration_date = Column(DateTime, default=datetime.utcnow)
    last_login_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    refresh_token = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    subscription_type = Column(
        SQLAlchemyEnum(SubscriptionType, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        server_default="free"
    )
    # subscription_type = Column(Enum(SubscriptionType), default=SubscriptionType.free, nullable=False)

    preferences = relationship("UserPreference", back_populates="user")
    documents = relationship("Document", back_populates="user")
    bookmarks = relationship("UserBookmark", back_populates="user")
    scanning_history = relationship("ScanningHistory", back_populates="user")
    accessibility = relationship("Accessibility", back_populates="user")
    activities = relationship("UserActivity", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")
    donations = relationship("Donation", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")
    # refunds = relationship("Refund",back_populates="user")
    refunds = relationship("Refund", back_populates="user", cascade="all, delete-orphan")
    