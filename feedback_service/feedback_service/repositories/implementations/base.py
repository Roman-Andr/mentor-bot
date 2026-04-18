"""Base SQLAlchemy repository implementation."""

from collections.abc import Sequence
from datetime import datetime
from typing import Any, TypeVar

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from feedback_service.repositories.interfaces.base import BaseRepository

T = TypeVar("T")
V = TypeVar("V", bound=int | str)


def apply_date_filters(
    query: Select[Any],
    model_class: type[T],
    from_date: datetime | None,
    to_date: datetime | None,
    date_column: str = "submitted_at",
) -> Select[Any]:
    """
    Apply date range filters to a query.

    Args:
        query: The SQLAlchemy select query
        model_class: The model class with the date column
        from_date: Start date (inclusive)
        to_date: End date (inclusive)
        date_column: Name of the date column to filter on

    Returns:
        The modified query with date filters applied
    """
    date_attr = getattr(model_class, date_column)

    if from_date:
        query = query.where(date_attr >= from_date)
    if to_date:
        query = query.where(date_attr <= to_date)

    return query


class DateFilterMixin:
    """Mixin providing date filter functionality for repositories."""

    def _apply_date_filters(
        self,
        query: Select[Any],
        model_class: type[T],
        from_date: datetime | None,
        to_date: datetime | None,
        date_column: str = "submitted_at",
    ) -> Select[Any]:
        """Apply date range filters to a query."""
        return apply_date_filters(query, model_class, from_date, to_date, date_column)


class SqlAlchemyBaseRepository[T, V: int | str](BaseRepository[T, V]):
    """Base SQLAlchemy repository implementation."""

    def __init__(self, session: AsyncSession, model_class: type[T]) -> None:
        """Initialize the repository with database session and model class."""
        self._session = session
        self._model_class = model_class

    async def get_by_id(self, entity_id: V) -> T | None:
        """Get entity by its primary key."""
        stmt = select(self._model_class).where(self._model_class.id == entity_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, *, skip: int = 0, limit: int = 100) -> Sequence[T]:
        """Get all entities with pagination."""
        stmt = select(self._model_class).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def create(self, entity: T) -> T:
        """Create new entity."""
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def update(self, entity: T) -> T:
        """Update existing entity."""
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def delete(self, entity_id: V) -> bool:
        """Delete entity by ID."""
        entity = await self.get_by_id(entity_id)
        if not entity:
            return False

        await self._session.delete(entity)
        await self._session.flush()
        return True
