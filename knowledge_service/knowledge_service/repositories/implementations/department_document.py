"""SQLAlchemy implementation of Department document repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from knowledge_service.models import DepartmentDocument
from knowledge_service.repositories.implementations.base import SqlAlchemyBaseRepository
from knowledge_service.repositories.interfaces.department_document import IDepartmentDocumentRepository


class DepartmentDocumentRepository(SqlAlchemyBaseRepository[DepartmentDocument, int], IDepartmentDocumentRepository):
    """SQLAlchemy implementation of Department document repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize department document repository."""
        super().__init__(session, DepartmentDocument)

    async def get_by_department(
        self, department_id: int, *, category: str | None = None, is_public: bool | None = None
    ) -> list[DepartmentDocument]:
        """Get all documents for a department, optionally filtered by category and visibility."""
        stmt = select(DepartmentDocument).where(DepartmentDocument.department_id == department_id)

        if category:
            stmt = stmt.where(DepartmentDocument.category == category)
        if is_public is not None:
            stmt = stmt.where(DepartmentDocument.is_public == is_public)

        stmt = stmt.order_by(DepartmentDocument.created_at.desc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_category(self, category: str) -> list[DepartmentDocument]:
        """Get all documents by category."""
        stmt = (
            select(DepartmentDocument)
            .where(DepartmentDocument.category == category)
            .order_by(DepartmentDocument.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
