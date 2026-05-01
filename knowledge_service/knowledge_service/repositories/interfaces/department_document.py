"""Department document repository interface."""

from abc import abstractmethod
from typing import TYPE_CHECKING

from knowledge_service.repositories.interfaces.base import BaseRepository

if TYPE_CHECKING:
    from knowledge_service.models.department_document import DepartmentDocument


class IDepartmentDocumentRepository(BaseRepository["DepartmentDocument", int]):
    """Department document repository interface."""

    @abstractmethod
    async def get_by_department(
        self, department_id: int, *, category: str | None = None, is_public: bool | None = None
    ) -> list[DepartmentDocument]:
        """Get all documents for a department, optionally filtered by category and visibility."""

    @abstractmethod
    async def get_by_category(self, category: str) -> list[DepartmentDocument]:
        """Get all documents by category."""
