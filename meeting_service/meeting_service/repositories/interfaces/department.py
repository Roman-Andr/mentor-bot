"""Department repository interface."""

from abc import abstractmethod

from meeting_service.models import Department
from meeting_service.repositories.interfaces.base import BaseRepository


class IDepartmentRepository(BaseRepository["Department", int]):
    """Department repository interface with department-specific queries."""

    @abstractmethod
    async def get_by_name(self, name: str) -> Department | None:
        """Get department by its name."""
