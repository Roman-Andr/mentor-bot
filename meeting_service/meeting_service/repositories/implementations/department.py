"""SQLAlchemy implementation of Department repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from meeting_service.models import Department
from meeting_service.repositories.implementations.base import SqlAlchemyBaseRepository
from meeting_service.repositories.interfaces.department import IDepartmentRepository


class DepartmentRepository(SqlAlchemyBaseRepository[Department, int], IDepartmentRepository):
    """SQLAlchemy implementation of Department repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize DepartmentRepository with database session."""
        super().__init__(session, Department)

    async def get_by_name(self, name: str) -> Department | None:
        """Get department by its name."""
        stmt = select(Department).where(Department.name == name)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
