from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse
from src.utils.logging import logger
from src.core.exceptions import (
    InvalidTokenError,
    PasswordTooWeakException,
    UserNotFoundError,
)


async def invalid_token_handler(
    request: Request,
    exc: InvalidTokenError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)}
    )


async def password_too_weak_handler(
    request: Request,
    exc: PasswordTooWeakException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )


async def user_not_found_handler(
    request: Request,
    exc: UserNotFoundError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)}
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers with the FastAPI application."""
    app.add_exception_handler(InvalidTokenError, invalid_token_handler)
    app.add_exception_handler(
        PasswordTooWeakException,
        password_too_weak_handler
    )
    app.add_exception_handler(UserNotFoundError, user_not_found_handler)

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.error("http_exception", detail=str(exc.detail), status_code=exc.status_code)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error("validation_error", errors=exc.errors())
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()},
        )

    @app.exception_handler(CustomAppException)
    async def custom_app_exception_handler(request: Request, exc: CustomAppException):
        logger.error("custom_app_exception", message=exc.message)
        return JSONResponse(
            status_code=500,
            content={"detail": exc.message},
        )
