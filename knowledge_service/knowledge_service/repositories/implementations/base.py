"""Base SQLAlchemy repository implementation."""

from collections.abc import Sequence
from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from knowledge_service.repositories.interfaces.base import BaseRepository

T = TypeVar("T")
I = TypeVar("I", bound=int | str)


class SqlAlchemyBaseRepository[T, I: int | str](BaseRepository[T, I]):
    """Base SQLAlchemy repository implementation."""

    def __init__(self, session: AsyncSession, model_class: type[T]) -> None:
        self._session = session
        self._model_class = model_class

    async def get_by_id(self, entity_id: I) -> T | None:
        stmt = select(self._model_class).where(self._model_class.id == entity_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, *, skip: int = 0, limit: int = 100) -> Sequence[T]:
        stmt = select(self._model_class).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def create(self, entity: T) -> T:
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def update(self, entity: T) -> T:
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def delete(self, entity_id: I) -> bool:
        entity = await self.get_by_id(entity_id)
        if not entity:
            return False
        await self._session.delete(entity)
        await self._session.flush()
        return True
