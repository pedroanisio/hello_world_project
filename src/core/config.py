# src/core/config.py
from typing import Any, ClassVar, Dict

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application Settings
    PROJECT_NAME: str  # Name of your project
    API_VERSION: str  # API version (e.g., "1.0.0")
    ENVIRONMENT: str = "dev"  # Environment setting (dev/test/prod) with default="dev"
    COMPOSE_PROJECT_NAME: str = "api"

    # Database Configuration
    DATABASE_URL: str  # Main database connection string
    TEST_DATABASE_URL: str  # Test database connection string
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "app"
    POSTGRES_HOST: str = "db"  # Default for production
    POSTGRES_TEST_HOST: str = "localhost"  # Add this for testing

    # Security Settings
    SECRET_KEY: str  # JWT/encryption secret key
    REFRESH_SECRET_KEY: str  # JWT refresh token secret key
    ALGORITHM: str = "HS256"  # JWT encryption algorithm (default="HS256")

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    LOGIN_RATE_LIMIT_REQUESTS: int = 20
    LOGIN_RATE_LIMIT_WINDOW: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    TOKEN_AUDIENCE: str = "your-app-users"
    TOKEN_ISSUER: str = "your-app-name"

    # Token type constants
    TOKEN_TYPE_ACCESS: ClassVar[str] = "access"  # nosec B105
    TOKEN_TYPE_REFRESH: ClassVar[str] = "refresh"  # nosec B105

    # Auth Settings
    AUTH_SECRET_KEY: str
    AUTH_REFRESH_SECRET_KEY: str
    AUTH_ALGORITHM: str = "HS256"
    AUTH_TOKEN_ISSUER: str = "fastapi-auth-service"
    AUTH_TOKEN_AUDIENCE: str = "fastapi-users"

    # CORS Configuration
    ALLOWED_ORIGINS: str  # Allowed origins for CORS (Cross-Origin Resource Sharing)

    # Redis Configuration
    REDIS_URL: str = "redis://redis:6379/0"  # Redis connection string with default

    # Logging Configuration
    LOG_LEVEL: str = "INFO"  # Logging level with default="INFO"

    # Server Settings
    HOST: str = "127.0.0.1"  # Default to localhost
    PORT: int = 8000

    @field_validator("POSTGRES_HOST", mode="before")
    @classmethod
    def validate_postgres_host(cls, v: str, info: Dict[str, Any]) -> str:
        """Use localhost for testing environment"""
        if info.data.get("ENVIRONMENT") == "test":
            return info.data.get("POSTGRES_TEST_HOST", "localhost")
        return v

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v: str, info: Dict[str, Any]) -> str:
        """Construct database URL based on environment"""
        if info.data.get("ENVIRONMENT") == "test":
            host = info.data.get("POSTGRES_TEST_HOST", "localhost")
            return f"postgresql://{info.data.get('POSTGRES_USER')}:{info.data.get('POSTGRES_PASSWORD')}@{host}:5432/{info.data.get('POSTGRES_DB')}"
        return v

    class Config:
        # Configuration for loading environment variables
        env_file = ".env"  # Specifies which env file to load
        env_file_encoding = "utf-8"  # Specifies the file encoding


# Create a global settings instance
settings = Settings()
