from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from prometheus_client import Counter, Histogram
import time
import structlog

from src.core.config import settings
from src.core.security import setup_security
from src.core.error_handlers import setup_exception_handlers
from src.api.v1.routers import api_router

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

# Structured logging
logger = structlog.get_logger()
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    description="""
    Hello World API - A production-ready FastAPI application.
    
    Features:
    - OAuth2 with JWT tokens
    - SQLAlchemy models with Alembic migrations
    - Docker support
    - Prometheus metrics
    - Structured logging
    """,
    docs_url=None,  # We'll create a custom docs endpoint
)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{settings.PROJECT_NAME} - API Documentation",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Enhanced structured logging for request
    logger.info(
        "incoming_request",
        path=request.url.path,
        method=request.method,
        client_ip=request.client.host,
    )
    
    response = await call_next(request)
    
    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.observe(time.time() - start_time)
    return response

@app.get("/health")
async def health_check():
    from src.db.session import check_db_connection
    health_status = {
        "status": "healthy",
        "database": "healthy" if await check_db_connection() else "unhealthy",
        "version": settings.API_VERSION,
    }
    if not all(status == "healthy" for status in health_status.values()):
        health_status["status"] = "unhealthy"
        return JSONResponse(status_code=503, content=health_status)
    return health_status

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    setup_security(app)
    setup_exception_handlers(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
