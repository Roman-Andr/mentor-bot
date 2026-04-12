"""Department management service with repository pattern."""

from datetime import UTC, datetime

from auth_service.core import ConflictException, NotFoundException
from auth_service.models import Department
from auth_service.repositories.unit_of_work import IUnitOfWork
from auth_service.schemas import DepartmentCreate, DepartmentUpdate
from auth_service.utils.department_sync import department_sync_client


class DepartmentService:
    """Service for department management operations."""

    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize department service with unit of work."""
        self._uow = uow

    async def get_department_by_id(self, department_id: int) -> Department:
        """Get department by ID."""
        department = await self._uow.departments.get_by_id(department_id)
        if not department:
            msg = "Department"
            raise NotFoundException(msg)
        return department

    async def get_departments(
        self,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> tuple[list[Department], int]:
        """Get paginated list of departments with filtering."""
        departments, total = await self._uow.departments.find_departments(
            skip=skip,
            limit=limit,
            search=search,
        )
        return list(departments), total

    async def create_department(self, department_data: DepartmentCreate) -> Department:
        """Create new department and sync to other services."""
        existing = await self._uow.departments.get_by_name(department_data.name)
        if existing:
            msg = "Department with this name already exists"
            raise ConflictException(msg)

        department = Department(
            name=department_data.name,
            description=department_data.description,
        )

        created = await self._uow.departments.create(department)

        await department_sync_client.sync_department(
            created.name,
            created.description,
        )

        return created

    async def update_department(self, department_id: int, department_data: DepartmentUpdate) -> Department:
        """Update department information."""
        department = await self.get_department_by_id(department_id)

        if department_data.name and department_data.name != department.name:
            existing = await self._uow.departments.get_by_name(department_data.name)
            if existing:
                msg = "Department with this name already exists"
                raise ConflictException(msg)
            department.name = department_data.name

        if department_data.description is not None:
            department.description = department_data.description

        department.updated_at = datetime.now(UTC)

        return await self._uow.departments.update(department)

    async def delete_department(self, department_id: int) -> None:
        """Delete department."""
        deleted = await self._uow.departments.delete(department_id)
        if not deleted:
            msg = "Department"
            raise NotFoundException(msg)
