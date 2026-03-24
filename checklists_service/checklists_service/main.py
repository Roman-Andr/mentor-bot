"""FastAPI application entry point for Checklists Service."""

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

from checklists_service.api import checklists, tasks, templates
from checklists_service.config import settings
from checklists_service.database import init_db
from checklists_service.middleware.auth import AuthTokenMiddleware
from checklists_service.schemas import HealthCheck, ServiceStatus
from checklists_service.utils import cache

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Handle application startup and shutdown events."""
    logger.info("Starting Checklists Service...")
    await init_db()

    # Connect to cache
    await cache.connect()

    logger.info("Database initialized")
    yield

    # Cleanup
    await cache.disconnect()
    logger.info("Shutting down Checklists Service...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Checklist Management Microservice",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
    redirect_slashes=False,
)

# Add middleware
# Rate-limit
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
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
app.include_router(templates.router, prefix=f"{settings.API_V1_PREFIX}/templates", tags=["templates"])
app.include_router(checklists.router, prefix=f"{settings.API_V1_PREFIX}/checklists", tags=["checklists"])
app.include_router(tasks.router, prefix=f"{settings.API_V1_PREFIX}/tasks", tags=["tasks"])


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
    # Check cache connection
    cache_status = "connected" if cache.is_connected else "disconnected"

    return HealthCheck(
        status="healthy",
        service="checklists",
        timestamp=datetime.now(UTC).isoformat(),
        dependencies={
            "database": "connected",
            "redis": cache_status,
            "auth_service": "connected",
        },
    )
