from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base

class AppSetting(Base):
    __tablename__ = 'app_settings'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    value = Column(String)
    last_updated = Column(DateTime)