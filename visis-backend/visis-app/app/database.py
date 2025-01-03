# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from app.core.config import settings

# SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URL

# engine = create_engine(SQLALCHEMY_DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# def init_db():
#     import app.models
#     import app.models.document
#     Base.metadata.create_all(bind=engine)


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()



# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URL

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL,
#     connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {},
# )

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL,
#     pool_size=20,            # Adjust based on your application's needs
#     max_overflow=0,          # Prevent exceeding pool_size
#     pool_timeout=360,         # Timeout for getting a connection
#     pool_recycle=2400,       # Recycle connections after 30 minutes
# )

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=80,            # Adjust based on your application's needs
    max_overflow=0,          # Prevent exceeding pool_size
    pool_timeout=1500,         # Timeout for getting a connection
    pool_recycle=2400,       # Recycle connections after 30 minutes
)



SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    import app.models
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
