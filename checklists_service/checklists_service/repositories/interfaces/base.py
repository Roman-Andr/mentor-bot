"""Base repository interface for common CRUD operations."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")
I = TypeVar("I", bound=int | str)


class BaseRepository[T, I: int | str](ABC):
    """Base repository interface for common CRUD operations."""

    @abstractmethod
    async def get_by_id(self, entity_id: I) -> T | None:
        """Get entity by its primary key."""

    @abstractmethod
    async def get_all(self, *, skip: int = 0, limit: int = 100) -> Sequence[T]:
        """Get all entities with pagination."""

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create new entity."""

    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update existing entity."""

    @abstractmethod
    async def delete(self, entity_id: I) -> bool:
        """Delete entity by ID."""
