from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse
from src.utils.logging import logger
from src.core.exceptions import PasswordTooWeakException, CustomAppException

def setup_exception_handlers(app: FastAPI):
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

    @app.exception_handler(PasswordTooWeakException)
    async def password_too_weak_handler(request: Request, exc: PasswordTooWeakException):
        logger.error("password_too_weak", message=exc.message)
        return JSONResponse(
            status_code=400,
            content={"detail": exc.message},
        )

    @app.exception_handler(CustomAppException)
    async def custom_app_exception_handler(request: Request, exc: CustomAppException):
        logger.error("custom_app_exception", message=exc.message)
        return JSONResponse(
            status_code=500,
            content={"detail": exc.message},
        )
