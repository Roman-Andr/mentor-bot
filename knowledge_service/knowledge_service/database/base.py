"""Database connection and session management."""

from collections.abc import AsyncGenerator

from sqlalchemy import Connection, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from knowledge_service.config import settings

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


# Declarative base
class Base(DeclarativeBase):
    """Base class for all database models."""


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
    """Create search indexes. Tables are managed by Alembic migrations."""
    async with engine.begin() as conn:
        await conn.run_sync(_create_search_indexes)


def _create_search_indexes(sync_conn: Connection) -> None:
    """Create full-text search indexes for PostgreSQL."""
    sync_conn.execute(
        text("""
        CREATE INDEX IF NOT EXISTS idx_articles_search_vector
        ON articles USING GIN(search_vector);
        """)
    )

    sync_conn.execute(
        text("""
        CREATE INDEX IF NOT EXISTS idx_articles_status
        ON articles(status);
        """)
    )

    sync_conn.execute(
        text("""
        CREATE INDEX IF NOT EXISTS idx_articles_department_id
        ON articles(department_id);
        """)
    )

    sync_conn.execute(
        text("""
        CREATE INDEX IF NOT EXISTS idx_articles_category_id
        ON articles(category_id);
        """)
    )

    sync_conn.execute(
        text("""
        CREATE INDEX IF NOT EXISTS idx_categories_parent_id
        ON categories(parent_id);
        """)
    )

    sync_conn.execute(
        text("""
        CREATE INDEX IF NOT EXISTS idx_article_views_article_id_viewed_at
        ON article_views(article_id, viewed_at DESC);
        """)
    )

    sync_conn.execute(
        text("""
        CREATE EXTENSION IF NOT EXISTS pg_trgm;
        """)
    )

    sync_conn.execute(
        text("""
        CREATE INDEX IF NOT EXISTS idx_articles_title_trgm
        ON articles USING GIN(title gin_trgm_ops);
        """)
    )

    sync_conn.execute(
        text("""
        CREATE INDEX IF NOT EXISTS idx_tags_name_trgm
        ON tags USING GIN(name gin_trgm_ops);
        """)
    )
