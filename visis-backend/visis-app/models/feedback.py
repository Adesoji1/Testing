from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    feedback_type = Column(String)
    content = Column(Text)
    submission_date = Column(DateTime)

    user = relationship("User", back_populates="feedbacks")