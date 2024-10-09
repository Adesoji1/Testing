from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Accessibility(Base):
    __tablename__ = 'accessibility'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    screen_reader_enabled = Column(Boolean)
    voice_commands_enabled = Column(Boolean)
    text_highlighting_enabled = Column(Boolean)

    user = relationship("User", back_populates="accessibility")