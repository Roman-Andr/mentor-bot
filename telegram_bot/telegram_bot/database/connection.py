"""Database connection and session management."""

import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from telegram_bot.config import settings
from telegram_bot.database.models import Base

metadata_obj = Base.metadata

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=40,
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
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database initialized")
