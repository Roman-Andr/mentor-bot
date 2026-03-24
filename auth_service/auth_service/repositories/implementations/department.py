"""SQLAlchemy implementation of Department repository."""

from typing import cast

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.models import Department
from auth_service.repositories.implementations.base import SqlAlchemyBaseRepository
from auth_service.repositories.interfaces.department import IDepartmentRepository


class DepartmentRepository(SqlAlchemyBaseRepository[Department, int], IDepartmentRepository):
    """SQLAlchemy implementation of Department repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize DepartmentRepository with database session."""
        super().__init__(session, Department)

    async def get_by_name(self, name: str) -> Department | None:
        """Get department by name."""
        stmt = select(Department).where(Department.name == name)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_departments(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> tuple[list[Department], int]:
        """Find departments with filtering and return results with total count."""
        count_stmt = select(func.count(Department.id))
        stmt = select(Department)

        if search:
            search_filter = or_(
                Department.name.ilike(f"%{search}%"),
                Department.description.ilike(f"%{search}%"),
            )
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        total_result = await self._session.execute(count_stmt)
        total = cast("int", total_result.scalar_one())

        stmt = stmt.offset(skip).limit(limit).order_by(Department.name.asc())
        result = await self._session.execute(stmt)
        departments = list(result.scalars().all())

        return departments, total
