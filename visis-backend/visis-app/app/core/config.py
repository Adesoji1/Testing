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

from pydantic_settings import BaseSettings
from pydantic import Field
import dotenv
import os

# Load environment variables from .env file
dotenv.load_dotenv()

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    """
    # Critical Settings
    SECRET_KEY: str = Field(..., description="The secret key used for signing tokens.")
    ALGORITHM: str = Field(..., description="The hashing algorithm for token encryption.")
    SQLALCHEMY_DATABASE_URL: str = Field(..., description="Database connection string.")
    
    # Email Configuration
    MAILTRAP_API_KEY: str = Field(None, description="API key for Mailtrap service.")
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: str = Field(..., description="AWS Access Key ID for S3 and other services.")
    AWS_SECRET_ACCESS_KEY: str = Field(..., description="AWS Secret Access Key for S3 and other services.")
    REGION_NAME: str = Field("us-east-1", description="Default AWS region for services.")
    S3_BUCKET_NAME: str = Field(..., description="The name of the S3 bucket for file storage.")
    S3_FOLDER_NAME: str = Field("uploads", description="The folder path inside the S3 bucket.")
    OPENAI_API_KEY: str = Field("OpenAI API key", description="Input your correct OpenAI API key")

    # REDIS_BROKER_URL: str = os.getenv("REDIS_BROKER_URL", "redis://localhost:6380/0")
    # REDIS_BACKEND_URL: str = os.getenv("REDIS_BACKEND_URL", "redis://localhost:6380/1")

    
    # File Upload Configuration
    MAX_UPLOAD_SIZE: int = Field(10 * 1024 * 1024, description="Maximum file upload size in bytes (default: 10 MB).")
    
    # Token Expiry Configuration
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = Field(
        15, description="Time in minutes before a password reset token expires."
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        30, description="Time in minutes before an access token expires."
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        7, description="Time in days before a refresh token expires."
    )

    class Config:
        env_file = ".env"

# Initialize settings
settings = Settings()
