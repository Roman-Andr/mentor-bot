"""Database connection and session management."""

from collections.abc import AsyncGenerator

from sqlalchemy import Connection, MetaData, schema, text
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
    """Create database schema and search indexes. Tables are managed by Alembic migrations."""
    async with engine.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: sync_conn.execute(schema.CreateSchema(settings.DATABASE_SCHEMA, if_not_exists=True))
        )
        await conn.run_sync(_create_search_indexes)


def _create_search_indexes(sync_conn: Connection) -> None:
    """Create full-text search indexes for PostgreSQL."""
    # Create search vector column for articles
    sync_conn.execute(
        text(f"""
        CREATE INDEX IF NOT EXISTS idx_articles_search_vector
        ON {settings.DATABASE_SCHEMA}.articles USING GIN(search_vector);
        """)
    )

    # Create indexes for common search filters
    sync_conn.execute(
        text(f"""
        CREATE INDEX IF NOT EXISTS idx_articles_status
        ON {settings.DATABASE_SCHEMA}.articles(status);
        """)
    )

    sync_conn.execute(
        text(f"""
        CREATE INDEX IF NOT EXISTS idx_articles_department_id
        ON {settings.DATABASE_SCHEMA}.articles(department_id);
        """)
    )

    sync_conn.execute(
        text(f"""
        CREATE INDEX IF NOT EXISTS idx_articles_category_id
        ON {settings.DATABASE_SCHEMA}.articles(category_id);
        """)
    )

    sync_conn.execute(
        text(f"""
        CREATE INDEX IF NOT EXISTS idx_categories_parent_id
        ON {settings.DATABASE_SCHEMA}.categories(parent_id);
        """)
    )

    sync_conn.execute(
        text(f"""
        CREATE INDEX IF NOT EXISTS idx_article_views_article_id_viewed_at
        ON {settings.DATABASE_SCHEMA}.article_views(article_id, viewed_at DESC);
        """)
    )

    # Create trigram indexes for fuzzy search
    sync_conn.execute(
        text("""
        CREATE EXTENSION IF NOT EXISTS pg_trgm;
        """)
    )

    sync_conn.execute(
        text(f"""
        CREATE INDEX IF NOT EXISTS idx_articles_title_trgm
        ON {settings.DATABASE_SCHEMA}.articles USING GIN(title gin_trgm_ops);
        """)
    )

    sync_conn.execute(
        text(f"""
        CREATE INDEX IF NOT EXISTS idx_tags_name_trgm
        ON {settings.DATABASE_SCHEMA}.tags USING GIN(name gin_trgm_ops);
        """)
    )
