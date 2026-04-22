"""FastAPI application entry point for Notification Service."""

import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from sqlalchemy import text

from notification_service.api import notifications, templates
from notification_service.api.endpoints import email
from notification_service.config import settings
from notification_service.database import engine, init_db
from notification_service.middleware.auth import AuthTokenMiddleware
from notification_service.schemas import HealthCheck, ServiceStatus
from notification_service.services.scheduler import scheduler

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Handle application startup and shutdown events."""
    logger.info("Starting Notification Service...")
    await init_db()

    # Start the background scheduler
    _scheduler_task = asyncio.create_task(scheduler.run())  # noqa: RUF006
    logger.info("Scheduler started")

    yield

    # Cleanup
    await scheduler.stop()
    logger.info("Shutting down Notification Service...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Notification and Reminder Management Microservice",
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

app.add_middleware(AuthTokenMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

# Include routers
app.include_router(notifications.router, prefix=f"{settings.API_V1_PREFIX}/notifications", tags=["notifications"])
app.include_router(email.router, prefix=f"{settings.API_V1_PREFIX}/email", tags=["email"])
app.include_router(templates.router, prefix=f"{settings.API_V1_PREFIX}/templates", tags=["templates"])


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
        service="notification",
        timestamp=datetime.now(UTC).isoformat(),
        dependencies={
            "database": db_status,
            "redis": "not_configured",  # Not used yet, could be added later
        },
    )
