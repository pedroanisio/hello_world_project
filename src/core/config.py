import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Hello World API"
    API_VERSION: str = "v1"
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/dbname"
    TEST_DATABASE_URL: str = "postgresql://user:password@localhost:5432/test_db"
    ALLOWED_ORIGINS: str = "http://localhost, http://127.0.0.1"
    SECRET_KEY: str = "REPLACE_ME_IN_ENV"
    REFRESH_SECRET_KEY: str = "REPLACE_ME_IN_ENV"
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings()
