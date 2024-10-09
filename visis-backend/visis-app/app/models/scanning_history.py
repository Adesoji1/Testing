from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class ScanningHistory(Base):
    __tablename__ = 'scanning_history'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    scan_type = Column(String)
    scan_content = Column(Text)
    scan_date = Column(DateTime)

    user = relationship("User", back_populates="scanning_history")