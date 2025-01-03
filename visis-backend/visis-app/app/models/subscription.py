# app/models/subscription.py

# from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
# from sqlalchemy.orm import relationship
# from datetime import datetime
# from app.database import Base

# class Subscription(Base):
#     __tablename__ = 'subscriptions'

#     id = Column(Integer, primary_key=True, index=True)
#     subscription_id = Column(String, unique=True, index=True)
#     subscription_code = Column(String, unique=True, index=True)
#     email_token = Column(String)
#     plan_code = Column(String)
#     amount = Column(Float)
#     currency = Column(String)
#     status = Column(String)
#     next_payment_date = Column(DateTime)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     user_id = Column(Integer, ForeignKey('users.id'))

#     user = relationship("User", back_populates="subscriptions")


# app/models/subscription.py

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String, unique=True, index=True, nullable=False)
    plan_code = Column(String, nullable=False)
    amount = Column(Float, nullable=False)  # Stored in Naira
    currency = Column(String, default="NGN", nullable=False)
    status = Column(String, default="active", nullable=False)
    start_date = Column(DateTime, nullable=False)
    next_payment_date = Column(DateTime, nullable=True)
    subscription_metadata = Column(JSON, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="subscriptions")
    subscription_code = Column(String, unique=True, index=True, nullable=False)
    transaction_data = Column(JSON, nullable=True)  # Store entire transaction response and logs

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))