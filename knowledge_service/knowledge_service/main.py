"""FastAPI application entry point for Knowledge Service."""

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

from knowledge_service.api import articles, attachments, categories, departments, dialogues, search, tags
from knowledge_service.config import settings
from knowledge_service.database import engine, init_db
from knowledge_service.middleware.auth import AuthTokenMiddleware
from knowledge_service.schemas import HealthCheck, ServiceStatus
from knowledge_service.utils import cache

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Handle application startup and shutdown events."""
    logger.info("Starting Knowledge Service...")
    await init_db()

    # Connect to cache
    await cache.connect()

    logger.info("Database initialized")
    yield

    # Cleanup
    await cache.disconnect()
    logger.info("Shutting down Knowledge Service...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Knowledge Base and FAQ Management Microservice",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
    redirect_slashes=False,
)

# Add middleware

# Rate-limit (disabled in debug mode)
if not settings.DEBUG:
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
app.include_router(categories.router, prefix=f"{settings.API_V1_PREFIX}/categories", tags=["categories"])
app.include_router(articles.router, prefix=f"{settings.API_V1_PREFIX}/articles", tags=["articles"])
app.include_router(search.router, prefix=f"{settings.API_V1_PREFIX}/search", tags=["search"])
app.include_router(tags.router, prefix=f"{settings.API_V1_PREFIX}/tags", tags=["tags"])
app.include_router(attachments.router, prefix=f"{settings.API_V1_PREFIX}", tags=["attachments"])
app.include_router(dialogues.router, prefix=f"{settings.API_V1_PREFIX}/dialogue-scenarios", tags=["dialogues"])
app.include_router(departments.router, prefix=f"{settings.API_V1_PREFIX}/departments", tags=["departments"])


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
    from sqlalchemy import text

    # Check database connectivity
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            db_status = "connected"
    except Exception:
        db_status = "disconnected"

    # Check cache connection
    cache_status = "connected" if cache.is_connected else "disconnected"

    return HealthCheck(
        status="healthy" if db_status == "connected" else "unhealthy",
        service="knowledge",
        timestamp=datetime.now(UTC).isoformat(),
        dependencies={
            "database": db_status,
            "redis": cache_status,
            "auth_service": "connected",
        },
    )
