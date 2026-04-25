"""Alembic environment configuration for feedback_service."""

import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

import feedback_service.models  # noqa: F401, E402 — registers all ORM models with Base.metadata
from feedback_service.config import settings as _settings  # noqa: E402
from feedback_service.database import Base  # noqa: E402

target_metadata = Base.metadata
_schema = target_metadata.schema


def get_url() -> str:
    """Get database URL from environment or settings."""
    return os.environ.get("DATABASE_URL", str(_settings.DATABASE_URL))


def include_name(name, type_, parent_names):  # type: ignore[no-untyped-def]
    """Filter objects to include only those in the service schema."""
    if type_ == "schema":
        return name == _schema
    return True


def run_migrations_offline() -> None:
    """Run migrations in offline mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):  # type: ignore[no-untyped-def]
    """Run migrations with given connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations asynchronously."""
    engine = create_async_engine(get_url(), poolclass=pool.NullPool)
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


def run_migrations_online() -> None:
    """Run migrations in online mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
