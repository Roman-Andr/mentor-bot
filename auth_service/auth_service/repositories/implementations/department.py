"""SQLAlchemy implementation of Department repository."""

from typing import cast

from sqlalchemy import Column, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.models import Department, User
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

    def _get_sort_column(self, sort_by: str | None) -> Column:
        """Get SQLAlchemy column for sorting."""
        column_map = {
            "name": Department.name,
            "description": Department.description,
            "createdAt": Department.created_at,
            "updatedAt": Department.updated_at,
        }
        return column_map.get(sort_by, Department.name)

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

        # Apply sorting
        sort_column = self._get_sort_column(sort_by)
        stmt = stmt.order_by(sort_column.asc() if sort_order.lower() == "asc" else sort_column.desc())

        stmt = stmt.offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        departments = list(result.scalars().all())

        return departments, total

    async def has_users(self, department_id: int) -> bool:
        """Check if department has any associated users."""
        stmt = select(func.count(User.id)).where(User.department_id == department_id)
        result = await self._session.execute(stmt)
        count = cast("int", result.scalar_one())
        return count > 0
