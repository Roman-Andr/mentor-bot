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
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> tuple[list[Department], int]:
        """Get paginated list of departments with filtering."""
        departments, total = await self._uow.departments.find_departments(
            skip=skip,
            limit=limit,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
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
        await self._uow.commit()

        await department_sync_client.sync_department(
            created.name,
            created.description,
        )

        return created

    async def update_department(self, department_id: int, department_data: DepartmentUpdate) -> Department:
        """Update department information and sync to other services."""
        department = await self.get_department_by_id(department_id)

        old_name = department.name
        name_changed = False

        if department_data.name and department_data.name != department.name:
            existing = await self._uow.departments.get_by_name(department_data.name)
            if existing:
                msg = "Department with this name already exists"
                raise ConflictException(msg)
            department.name = department_data.name
            name_changed = True

        if department_data.description is not None:
            department.description = department_data.description

        department.updated_at = datetime.now(UTC)

        updated = await self._uow.departments.update(department)

        if name_changed or department_data.description is not None:
            await department_sync_client.sync_department_update(
                old_name,
                updated.name,
                updated.description,
            )

        return updated

    async def delete_department(self, department_id: int) -> None:
        """Delete department and sync deletion to other services."""
        department = await self.get_department_by_id(department_id)
        department_name = department.name

        has_users = await self._uow.departments.has_users(department_id)
        if has_users:
            msg = "Cannot delete department with assigned users"
            raise ConflictException(msg)

        deleted = await self._uow.departments.delete(department_id)
        if not deleted:
            msg = "Department"
            raise NotFoundException(msg)

        await department_sync_client.sync_department_delete(department_name)
