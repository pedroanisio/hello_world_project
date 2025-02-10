import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "{{api-name}}"
    API_VERSION: str = "v1"
    DATABASE_URL: str
    TEST_DATABASE_URL: str = "postgresql://user:password@localhost:5432/test_db"
    ALLOWED_ORIGINS: str = "http://localhost, http://127.0.0.1"
    SECRET_KEY: str
    REFRESH_SECRET_KEY: str = "REPLACE_ME_IN_ENV"
    ALGORITHM: str = "HS256"

    class Config:
        env_files = [
            ".env.test",
            ".env.dev", 
            ".env.prod"
        ]
        env_file = f".env.{os.getenv('ENVIRONMENT', 'dev')}"

settings = Settings()
