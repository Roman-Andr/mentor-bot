"""FastAPI application entry point for Auth Service."""

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
from sqlalchemy.exc import SQLAlchemyError

from auth_service.api import audit, auth, departments, invitations, password_reset, user_mentors, users
from auth_service.config import settings
from auth_service.core import UserRole
from auth_service.database import AsyncSessionLocal, engine, init_db
from auth_service.middleware.request_id import RequestIDMiddleware
from auth_service.repositories.unit_of_work import SqlAlchemyUnitOfWork
from auth_service.schemas import HealthCheck, ServiceStatus, UserCreate
from auth_service.services.user import UserService
from auth_service.utils.integrations import checklists_service_client, notification_service_client
from auth_service.utils.logging import configure_logging

configure_logging(service_name="auth_service", log_level=settings.LOG_LEVEL)


async def create_default_admin_user() -> None:
    """Create default admin user if it doesn't exist."""
    async with SqlAlchemyUnitOfWork(AsyncSessionLocal) as uow:
        user_service = UserService(uow)
        existing_admin = await user_service.get_user_by_email(settings.ADMIN_EMAIL)

        if not existing_admin:
            logger.info("Creating default admin user: {}", settings.ADMIN_EMAIL)
            admin_data = UserCreate(
                email=settings.ADMIN_EMAIL,
                first_name="Admin",
                last_name="User",
                employee_id="ADMIN001",
                password=settings.ADMIN_PASSWORD,
                role=UserRole.ADMIN,
            )
            await user_service.create_user(admin_data)
            logger.info("Default admin user created successfully")
        else:
            logger.info("Default admin user already exists: {}", settings.ADMIN_EMAIL)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Handle application startup and shutdown events."""
    logger.info("Starting Auth Service...")
    await init_db()
    logger.info("Database initialized")
    await create_default_admin_user()
    logger.info("Default admin user check completed")
    yield
    logger.info("Shutting down Auth Service...")
    await checklists_service_client.aclose()
    await notification_service_client.aclose()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Authentication and User Management Microservice",
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
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
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
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["authentication"])
app.include_router(users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["users"])
app.include_router(invitations.router, prefix=f"{settings.API_V1_PREFIX}/invitations", tags=["invitations"])
app.include_router(departments.router, prefix=f"{settings.API_V1_PREFIX}/departments", tags=["departments"])
app.include_router(user_mentors.router, prefix=f"{settings.API_V1_PREFIX}/user-mentors", tags=["user-mentors"])
app.include_router(password_reset.router, prefix=f"{settings.API_V1_PREFIX}/password-reset", tags=["password-reset"])
app.include_router(audit.router, prefix=f"{settings.API_V1_PREFIX}/auth/audit", tags=["audit"])


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
    except SQLAlchemyError:
        logger.exception("Health check: database connectivity failed")
        db_status = "disconnected"

    return HealthCheck(
        status="healthy" if db_status == "connected" else "unhealthy",
        service="auth",
        timestamp=datetime.now(UTC).isoformat(),
        dependencies={
            "database": db_status,
            "redis": "connected" if hasattr(settings, "REDIS_URL") else "not_configured",
        },
    )
