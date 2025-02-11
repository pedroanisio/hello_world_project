from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from src.utils.logging import logger
from src.core.security import verify_password, verify_token
from src.core.token_manager import (
    create_access_token,
    create_refresh_token,
    decode_token,
    invalidate_token,
)
from src.db.repositories import get_user_by_email
from src.db.session import get_db
from src.core.exceptions import InvalidTokenError
from src.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = get_user_by_email(db, form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Create tokens with user claims and type
    claims = {"user_id": user.id, "type": "access"}  # Explicitly set token type
    access_token = create_access_token(claims)
    refresh_token = create_refresh_token(claims)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh")
async def refresh_token_endpoint(token: str = Depends(oauth2_scheme)):
    try:
        # Verify and decode refresh token
        logger.info("Attempting to refresh token")
        payload = decode_token(token, token_type="refresh")
        user_id = payload.get("user_id")

        # Create new access token
        new_access_token = create_access_token({"user_id": user_id})
        logger.info(f"Created new access token for user {user_id}")

        # Invalidate the old access token if present in payload
        if "access_token" in payload:
            logger.info("Found old access token in refresh payload, invalidating...")
            invalidate_token(payload["access_token"])
        else:
            logger.warning("No access token found in refresh token payload")

        # Invalidate the used refresh token
        logger.info("Invalidating used refresh token")
        invalidate_token(token)

        return {"access_token": new_access_token, "token_type": "bearer"}
    except InvalidTokenError as e:
        logger.error(f"Invalid token error during refresh: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )


@router.get("/protected")
async def protected_route(token: str = Depends(oauth2_scheme)):
    if not verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    return {"status": "success"}


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    # In a real implementation, you might want to blacklist the token
    return {"status": "success"}
