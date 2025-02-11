import re
from datetime import datetime
from typing import Optional, Dict, Set, Any

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
from fastapi import HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from starlette.middleware.base import BaseHTTPMiddleware
from passlib.context import CryptContext
from src.core.config import settings
from src.utils.logging import logger

# Initialize security tools with consistent configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
password_hasher = PasswordHasher()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_password_hash(password: str) -> str:
    """Hash a password using Argon2."""
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash using Argon2."""
    try:
        return password_hasher.verify(hashed_password, plain_password)
    except (VerifyMismatchError, InvalidHashError):
        return False


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware for authentication endpoints."""

    def __init__(self, app, max_requests: int = 5, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = {}

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting in test environment
        if settings.ENVIRONMENT == "test":
            return await call_next(request)

        if request.url.path in ["/api/v1/auth/login", "/api/v1/auth/refresh"]:
            client_ip = request.client.host
            now = datetime.utcnow()

            # Clean old requests
            if client_ip in self.requests:
                self.requests[client_ip] = [
                    ts
                    for ts in self.requests[client_ip]
                    if (now - ts).total_seconds() < self.window_seconds
                ]

            # Check rate limit
            if len(self.requests.get(client_ip, [])) >= self.max_requests:
                raise HTTPException(
                    status_code=429, detail="Too many requests. Please try again later."
                )

            # Record request
            if client_ip not in self.requests:
                self.requests[client_ip] = []
            self.requests[client_ip].append(now)

        return await call_next(request)
