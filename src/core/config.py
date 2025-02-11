# src/core/config.py
from pydantic import BaseSettings, validator
from typing import Dict, Any

class Settings(BaseSettings):
    PROJECT_NAME: str
    API_VERSION: str
    ENVIRONMENT: str = "dev"
    
    # Database
    DATABASE_URL: str
    TEST_DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    
    # CORS
    ALLOWED_ORIGINS: str
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v: str, values: Dict[str, Any]) -> str:
        if values.get("ENVIRONMENT") == "test":
            return values.get("TEST_DATABASE_URL", v)
        return v

    class Config:
        # If you're always using Docker and all vars are set,
        # you can omit env_file and customise_sources.
        pass

settings = Settings()
