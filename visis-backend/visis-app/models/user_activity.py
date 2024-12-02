# from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
# from sqlalchemy.orm import relationship
# from app.database import Base
# from datetime import datetime

# class UserActivity(Base):
#     __tablename__ = 'user_activity'
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey('users.id'))
#     activity_type = Column(String)
#     activity_details = Column(Text)
#     timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

#     # timestamp = Column(DateTime)

#     user = relationship("User", back_populates="activities")


# app/models/user_activity.py

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class UserActivity(Base):
    __tablename__ = 'user_activities'  # Changed to plural for consistency
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    activity_type = Column(String, nullable=False)
    activity_details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="activities")
