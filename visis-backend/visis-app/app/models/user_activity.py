from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class UserActivity(Base):
    __tablename__ = 'user_activity'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    activity_type = Column(String)
    activity_details = Column(Text)
    timestamp = Column(DateTime)

    user = relationship("User", back_populates="activities")