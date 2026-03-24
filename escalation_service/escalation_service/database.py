"""Database connection and session management."""

from collections.abc import AsyncGenerator

from sqlalchemy import MetaData, schema
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from escalation_service.config import settings

# Create async engine
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DEBUG,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Declarative metadata
metadata_obj = MetaData(schema=settings.DATABASE_SCHEMA)


# Declarative base
class Base(DeclarativeBase):
    """Base class for all database models."""

    metadata = metadata_obj


async def get_db() -> AsyncGenerator[AsyncSession]:
    """Dependency for getting async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        # Create schema if it does not exist
        await conn.run_sync(
            lambda sync_conn: sync_conn.execute(schema.CreateSchema(settings.DATABASE_SCHEMA, if_not_exists=True))
        )

        # Create all tables
        from escalation_service.models import EscalationRequest  # noqa: F401, PLC0415

        await conn.run_sync(Base.metadata.create_all)
