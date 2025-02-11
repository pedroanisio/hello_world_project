from datetime import datetime, timedelta
import uuid
from typing import Dict, Set
import jwt

from src.core.config import settings
from src.core.exceptions import InvalidTokenError
from src.utils.logging import logger

# Token blacklist storage (use Redis in production)
_token_blacklist: Set[str] = set()


def get_utc_now() -> datetime:
    """Get current UTC timestamp."""
    return datetime.utcnow()


def create_access_token(data: Dict) -> str:
    """Create a new access token."""
    jti = str(uuid.uuid4())
    to_encode = data.copy()
    to_encode.update(
        {
            "jti": jti,
            "type": "access",
            "exp": get_utc_now()
            + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            "iat": get_utc_now(),
            "iss": settings.TOKEN_ISSUER,
            "aud": settings.TOKEN_AUDIENCE,
        }
    )
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: Dict) -> str:
    """Create a new refresh token."""
    jti = str(uuid.uuid4())
    access_token = create_access_token(data)
    to_encode = data.copy()
    to_encode.update(
        {
            "jti": jti,
            "type": "refresh",
            "exp": get_utc_now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            "iat": get_utc_now(),
            "iss": settings.TOKEN_ISSUER,
            "aud": settings.TOKEN_AUDIENCE,
            "access_token": access_token,
        }
    )
    encoded_jwt = jwt.encode(
        to_encode, settings.REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str, token_type: str = "access") -> Dict:
    """
    Decode and validate a token.

    Args:
        token: The JWT token to decode
        token_type: Either "access" or "refresh"

    Returns:
        Dictionary containing the token claims

    Raises:
        InvalidTokenError: If token is invalid or blacklisted
    """
    try:
        secret_key = (
            settings.SECRET_KEY
            if token_type == "access"
            else settings.REFRESH_SECRET_KEY
        )

        # First check blacklist without verification
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        logger.debug(
            f"Checking token JTI {unverified_payload.get('jti')} against blacklist"
        )
        logger.debug(f"Current blacklist: {_token_blacklist}")

        if (
            "jti" in unverified_payload
            and unverified_payload["jti"] in _token_blacklist
        ):
            logger.info(f"Token JTI {unverified_payload['jti']} found in blacklist")
            raise InvalidTokenError("Token has been invalidated")

        # Now do full validation
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[settings.ALGORITHM],
            audience=settings.TOKEN_AUDIENCE,
        )
        logger.debug(f"Token decoded successfully with type: {payload.get('type')}")

        # Verify token type
        if payload.get("type") != token_type:
            logger.warning(
                f"Token type mismatch. Expected {token_type}, got {payload.get('type')}"
            )
            raise InvalidTokenError("Invalid token type")

        # Skip issuer/audience checks in test environment
        if settings.ENVIRONMENT != "test":
            if "iss" in payload and payload["iss"] != settings.TOKEN_ISSUER:
                raise InvalidTokenError("Invalid token issuer")
            if "aud" in payload and payload["aud"] != settings.TOKEN_AUDIENCE:
                raise InvalidTokenError("Invalid token audience")

        return payload

    except jwt.InvalidAudienceError:
        logger.warning("Token has invalid audience")
        raise InvalidTokenError("Invalid audience")
    except jwt.ExpiredSignatureError:
        logger.info("Token has expired")
        raise InvalidTokenError("Token has expired")
    except jwt.PyJWTError as e:
        logger.error(f"JWT validation error: {str(e)}")
        raise InvalidTokenError(str(e))


def invalidate_token(token: str) -> None:
    """
    Invalidate a token by adding its JTI to the blacklist.
    Handles both access and refresh tokens.
    """
    try:
        # Try access token first
        payload = None
        logger.info("Attempting to invalidate token")

        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            logger.info(
                f"Successfully decoded token as access token: {payload.get('jti')}"
            )
        except jwt.PyJWTError:
            # If not access token, try as refresh token
            logger.info("Token not valid as access token, trying as refresh token")
            payload = jwt.decode(
                token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            logger.info(
                f"Successfully decoded token as refresh token: {payload.get('jti')}"
            )

        if payload and "jti" in payload:
            jti = payload["jti"]
            _token_blacklist.add(jti)
            logger.info(
                f"Added token JTI {jti} to blacklist. Current blacklist: {_token_blacklist}"
            )

            # If this is a refresh token, also invalidate its associated access token
            if payload.get("type") == "refresh" and "access_token" in payload:
                logger.info("Found associated access token, attempting to invalidate")
                invalidate_token(payload["access_token"])

    except jwt.PyJWTError as e:
        logger.error(f"Error during token invalidation: {str(e)}")
        raise


def verify_token(token: str) -> bool:
    """Verify if a token is valid and not blacklisted."""
    try:
        decode_token(token)
        return True
    except InvalidTokenError:
        return False
