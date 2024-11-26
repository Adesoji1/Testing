# from pydantic_settings import BaseSettings
# import dotenv
# import os

# dotenv.load_dotenv()

# class Settings(BaseSettings):
#     SECRET_KEY: str = os.getenv("SECRET_KEY")
#     ALGORITHM: str = os.getenv("ALGORITHM")
#     SQLALCHEMY_DATABASE_URL: str = os.getenv("SQLALCHEMY_DATABASE_URL")
#     MAILTRAP_API_KEY: str = os.getenv("MAILTRAP_API_KEY")
#     AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID")
#     AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY")
#     REGION_NAME: str = os.getenv("REGION_NAME")
#     S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME")
#     S3_FOLDER_NAME: str = os.getenv("S3_FOLDER_NAME")
#     MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE"))
#     PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("PASSWORD_RESET_TOKEN_EXPIRE_MINUTES"))
#     ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
#     REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))
    
    

#     class Config:
#         env_file = ".env"

# settings = Settings()
# app/core/config.py

# app/core/config.py

from pydantic_settings import BaseSettings
from pydantic import Field
import dotenv
import os
from typing import Optional

dotenv.load_dotenv()

class Settings(BaseSettings):
    # Authentication & Security
    SECRET_KEY: str = Field(..., description="Secret key for token signing")
    ALGORITHM: str = Field(default="HS256", description="Hashing algorithm for token encryption")
    
    # Database
    SQLALCHEMY_DATABASE_URL: str = Field(..., description="Database connection string")
    
    # Email
    MAILTRAP_API_KEY: Optional[str] = Field(None, description="Mailtrap API key")
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: str = Field(..., description="AWS Access Key ID")
    AWS_SECRET_ACCESS_KEY: str = Field(..., description="AWS Secret Access Key")
    REGION_NAME: str = Field(default="us-east-1", description="AWS region name")  # Keep REGION_NAME for backwards compatibility
    S3_BUCKET_NAME: str = Field(..., description="S3 bucket name")
    S3_FOLDER_NAME: str = Field(default="uploads", description="S3 folder path")
    
    # AI Services
    GEMINI_API_KEY: str = Field(..., description="Google Gemini API key")
    OPENAI_API_KEY: Optional[str] = Field(None, description="OpenAI API key")
    
    # File Upload
    MAX_UPLOAD_SIZE: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Maximum upload size in bytes"
    )
    
    # Token Configuration
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = Field(default=15, description="Password reset token expiry")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiry")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh token expiry")

    # Property for AWS_REGION compatibility
    @property
    def AWS_REGION(self) -> str:
        return self.REGION_NAME

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

# Initialize settings
settings = Settings()