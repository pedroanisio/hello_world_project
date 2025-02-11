# src/core/config.py
from typing import Any, Dict

from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    # Application Settings
    PROJECT_NAME: str  # Name of your project
    API_VERSION: str  # API version (e.g., "1.0.0")
    ENVIRONMENT: str = "dev"  # Environment setting (dev/test/prod) with default="dev"

    # Database Configuration
    DATABASE_URL: str  # Main database connection string
    TEST_DATABASE_URL: str  # Test database connection string

    # Security Settings
    SECRET_KEY: str  # JWT/encryption secret key
    REFRESH_SECRET_KEY: str  # JWT refresh token secret key
    ALGORITHM: str = "HS256"  # JWT encryption algorithm (default="HS256")

    # CORS Configuration
    ALLOWED_ORIGINS: str  # Allowed origins for CORS (Cross-Origin Resource Sharing)

    # Redis Configuration
    REDIS_URL: str = "redis://redis:6379/0"  # Redis connection string with default

    # Logging Configuration
    LOG_LEVEL: str = "INFO"  # Logging level with default="INFO"

    # New settings
    HOST: str = "127.0.0.1"  # Default to localhost
    PORT: int = 8000

    # Validator method
    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v: str, values: Dict[str, Any]) -> str:
        # If environment is "test", use TEST_DATABASE_URL instead
        if values.get("ENVIRONMENT") == "test":
            return values.get("TEST_DATABASE_URL", v)
        return v

    class Config:
        # Configuration for loading environment variables
        env_file = ".env"  # Specifies which env file to load
        env_file_encoding = "utf-8"  # Specifies the file encoding


# Create a global settings instance
settings = Settings()
