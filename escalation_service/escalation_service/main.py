"""FastAPI application entry point for Escalation Service."""

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

from escalation_service.api.endpoints import escalations_router
from escalation_service.config import settings
from escalation_service.database import engine, init_db
from escalation_service.schemas import HealthCheck, ServiceStatus

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Handle application startup and shutdown events."""
    logger.info("Starting Escalation Service...")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down Escalation Service...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Escalation Request Management Microservice",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
    redirect_slashes=False,
)

# Rate limiting (disabled in debug mode)
if not settings.DEBUG:
    limiter = Limiter(key_func=get_remote_address, default_limits=["100/second"])
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted hosts
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

# Include routers
app.include_router(escalations_router, prefix=f"{settings.API_V1_PREFIX}/escalations", tags=["escalations"])


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
        service="escalation",
        timestamp=datetime.now(UTC).isoformat(),
        dependencies={
            "database": db_status,
        },
    )
