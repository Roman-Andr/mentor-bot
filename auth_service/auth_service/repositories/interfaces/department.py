"""Department repository interface."""

from abc import abstractmethod

from auth_service.models import Department
from auth_service.repositories.interfaces.base import BaseRepository


class IDepartmentRepository(BaseRepository["Department", int]):
    """Department repository interface."""

    @abstractmethod
    async def get_by_name(self, name: str) -> Department | None:
        """Get department by name."""

    @abstractmethod
    async def find_departments(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> tuple[list[Department], int]:
        """Find departments with filtering and return results with total count."""
