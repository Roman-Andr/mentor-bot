"""FastAPI application entry point for Knowledge Service."""

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

from knowledge_service.api import analytics, articles, attachments, audit, categories, dialogues, search, search_analytics, tags
from knowledge_service.config import settings
from knowledge_service.database import engine, init_db
from knowledge_service.middleware.auth import AuthTokenMiddleware
from knowledge_service.middleware.request_id import RequestIDMiddleware
from knowledge_service.schemas import HealthCheck, ServiceStatus
from knowledge_service.services.cleanup import cleanup_old_search_history
from knowledge_service.utils import cache
from knowledge_service.utils.logging import configure_logging

configure_logging(service_name="knowledge_service", log_level=settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Handle application startup and shutdown events."""
    logger.info("Starting Knowledge Service...")
    await init_db()

    # Connect to cache
    await cache.connect()

    # Cleanup old search history on startup
    try:
        deleted_count = await cleanup_old_search_history()
        logger.info(f"Cleaned up {deleted_count} old search history records on startup")
    except Exception as e:
        logger.warning(f"Failed to cleanup old search history on startup: {e}")

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
app.add_middleware(RequestIDMiddleware)

# Include routers
app.include_router(categories.router, prefix=f"{settings.API_V1_PREFIX}/categories", tags=["categories"])
app.include_router(articles.router, prefix=f"{settings.API_V1_PREFIX}/articles", tags=["articles"])
app.include_router(search.router, prefix=f"{settings.API_V1_PREFIX}/search", tags=["search"])
app.include_router(search_analytics.router, prefix=f"{settings.API_V1_PREFIX}/knowledge/search-analytics", tags=["search-analytics"])
app.include_router(tags.router, prefix=f"{settings.API_V1_PREFIX}/tags", tags=["tags"])
app.include_router(attachments.router, prefix=f"{settings.API_V1_PREFIX}", tags=["attachments"])
app.include_router(dialogues.router, prefix=f"{settings.API_V1_PREFIX}/dialogue-scenarios", tags=["dialogues"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_PREFIX}/knowledge/analytics", tags=["analytics"])
app.include_router(audit.router, prefix=f"{settings.API_V1_PREFIX}/knowledge/audit", tags=["audit"])


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
