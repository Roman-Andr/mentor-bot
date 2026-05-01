"""FastAPI application entry point for Meeting Service."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from loguru import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from sqlalchemy import text

from meeting_service.api.endpoints import audit_router, calendar_router, meetings_router, user_meetings_router
from meeting_service.config import settings
from meeting_service.database import engine, init_db
from meeting_service.middleware.request_id import RequestIDMiddleware
from meeting_service.schemas import HealthCheck, ServiceStatus
from meeting_service.utils.logging import configure_logging

configure_logging(service_name="meeting_service", log_level=settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Handle application startup and shutdown events."""
    logger.info("Starting Meeting Service...")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down Meeting Service...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Meeting and Appointment Management Microservice",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
    redirect_slashes=False,
)

# Add middleware

# Rate-limit (disabled in debug mode)
if not settings.DEBUG:
    limiter = Limiter(key_func=get_remote_address, default_limits=["100/second"])
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
app.add_middleware(RequestIDMiddleware)

# Include routers
app.include_router(meetings_router, prefix=f"{settings.API_V1_PREFIX}/meetings", tags=["meetings"])
app.include_router(user_meetings_router, prefix=f"{settings.API_V1_PREFIX}/user-meetings", tags=["user-meetings"])
app.include_router(calendar_router, prefix=f"{settings.API_V1_PREFIX}/calendar", tags=["calendar"])
app.include_router(audit_router, prefix=f"{settings.API_V1_PREFIX}/meetings/audit", tags=["audit"])


@app.get("/")
async def root() -> ServiceStatus:
    """Root endpoint returning service status."""
    return ServiceStatus(
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        status="running",
        docs="/docs" if settings.DEBUG else None,
    )


@app.get("/health")
async def health_check() -> HealthCheck:
    """Health check endpoint for load balancers and monitoring."""
    # Check database connectivity
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return HealthCheck(
        status="healthy" if db_status == "connected" else "unhealthy",
        service="meeting",
        timestamp=datetime.now(UTC).isoformat(),
        dependencies={
            "database": db_status,
            "auth_service": "enabled",
        },
    )
