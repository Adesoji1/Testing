# # app/models/transaction.py

# from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey,Text
# from sqlalchemy.orm import relationship
# from datetime import datetime
# from app.database import Base

# class Transaction(Base):
#     __tablename__ = 'transactions'

#     id = Column(Integer, primary_key=True, index=True)
#     transaction_id = Column(String, unique=True, index=True,nullable=True)
#     reference = Column(String, unique=True, index=True,nullable=False)
#     amount = Column(Float,nullable=True)
#     currency = Column(String,nullable=True)
#     status = Column(String,nullable=True)
#     paid_at = Column(DateTime,nullable=True)
#     channel = Column(String,nullable=True)
#     customer_email = Column(String,nullable=True)
#     customer_id = Column(Integer,nullable=True)
#     authorization_code = Column(String, nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     user_id = Column(Integer, ForeignKey('users.id'))

#     user = relationship("User", back_populates="transactions")





# app/models/transaction.py

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True, nullable=True)  # Made nullable
    reference = Column(String, unique=True, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    status = Column(String, nullable=False)
    paid_at = Column(DateTime, nullable=True)
    channel = Column(String, nullable=True)
    customer_email = Column(String, nullable=False)
    customer_id = Column(Integer, nullable=True)
    authorization_code = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship("User", back_populates="transactions")



 

    
   