from sqlalchemy import Column, Integer, String
from app.database import Base

class Bank(Base):
    __tablename__ = 'banks'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False)
    country_code = Column(String, nullable=False)
    # Add additional fields as needed
