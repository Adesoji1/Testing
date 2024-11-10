from pydantic_settings import BaseSettings
import dotenv
import os

dotenv.load_dotenv()

class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    SQLALCHEMY_DATABASE_URL: str = os.getenv("SQLALCHEMY_DATABASE_URL")
    MAILTRAP_API_KEY: str = os.getenv("MAILTRAP_API_KEY")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY")
    REGION_NAME: str = os.getenv("REGION_NAME")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME")
    S3_FOLDER_NAME: str = os.getenv("S3_FOLDER_NAME")
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE"))
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("PASSWORD_RESET_TOKEN_EXPIRE_MINUTES"))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))
    
    

    class Config:
        env_file = ".env"

settings = Settings()