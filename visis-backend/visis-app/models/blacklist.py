from datetime import timezone
from sqlalchemy import Column, String, DateTime
from datetime import datetime
from app.database import Base

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"

    token = Column(String, primary_key=True, unique=True, index=True)
    blacklisted_on = Column(DateTime, default=datetime.now(tz=timezone.utc))
