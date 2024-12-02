# app/core/config.py


from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
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

    # TTS API Key for CAMB.AI
    TTS_API_KEY: str = Field(..., description="CAMB.AI Text-to-Speech API key")
    
    # File Upload
    MAX_UPLOAD_SIZE: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Maximum upload size in bytes"
    )
    
    # Token Configuration
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = Field(default=15, description="Password reset token expiry")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiry")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh token expiry")

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_CACHE_TTL: int = 80640 # Cache TTL in seconds (e.g., 55 days)

    #Paystack configuration
    PAYSTACK_SECRET_KEY: str = os.getenv("PAYSTACK_SECRET_KEY")
    PAYSTACK_PUBLIC_KEY: str = os.getenv("PAYSTACK_PUBLIC_KEY")
    PAYSTACK_CALLBACK_URL: str = os.getenv("PAYSTACK_CALLBACK_URL")  # URL where Paystack redirects after payment
    PAYSTACK_PLAN_CODE: str = os.getenv("PAYSTACK_PLAN_CODE")  # Your Plan Code

    # Email configuration
    EMAIL_HOST: str = Field("sandbox.smtp.mailtrap.io", env="EMAIL_HOST")
    EMAIL_PORT: int = Field(2525, env="EMAIL_PORT")  # Default port
    EMAIL_HOST_USER: str = Field(..., env="EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD: str = Field(..., env="EMAIL_HOST_PASSWORD")
    EMAIL_USE_TLS: bool = Field(True, env="EMAIL_USE_TLS")
    EMAIL_FROM: str = Field("no-reply@vinsighte.com.ng", env="EMAIL_FROM")

    @field_validator("EMAIL_PORT",mode="before")
    def parse_email_port(cls, value):
        """Strip and parse EMAIL_PORT to an integer, ensuring it is valid."""
        try:
            return int(str(value).strip().split()[0])  # Extracts the first numeric part
        except ValueError:
            raise ValueError(f"Invalid EMAIL_PORT: {value}. Ensure it is a valid integer.")

    
  

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