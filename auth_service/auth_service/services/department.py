"""Department management service with repository pattern."""

from datetime import UTC, datetime

from loguru import logger

from auth_service.core import ConflictException, NotFoundException
from auth_service.models import Department
from auth_service.repositories.unit_of_work import IUnitOfWork
from auth_service.schemas import DepartmentCreate, DepartmentUpdate


class DepartmentService:
    """Service for department management operations."""

    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize department service with unit of work."""
        self._uow = uow

    async def get_department_by_id(self, department_id: int) -> Department:
        """Get department by ID."""
        logger.debug("Fetching department by id={}", department_id)
        department = await self._uow.departments.get_by_id(department_id)
        if not department:
            logger.warning("Department not found (department_id={})", department_id)
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
        """Create new department."""
        logger.debug("Creating department (name={})", department_data.name)
        existing = await self._uow.departments.get_by_name(department_data.name)
        if existing:
            logger.warning("Create department conflict: name already exists ({})", department_data.name)
            msg = "Department with this name already exists"
            raise ConflictException(msg)

        department = Department(
            name=department_data.name,
            description=department_data.description,
        )

        created = await self._uow.departments.create(department)
        await self._uow.commit()
        logger.info("Department created (department_id={}, name={})", created.id, created.name)
        return created

    async def update_department(self, department_id: int, department_data: DepartmentUpdate) -> Department:
        """Update department information."""
        logger.debug("Updating department (department_id={})", department_id)
        department = await self.get_department_by_id(department_id)

        if department_data.name and department_data.name != department.name:
            existing = await self._uow.departments.get_by_name(department_data.name)
            if existing:
                logger.warning(
                    "Update department conflict: name already exists ({})",
                    department_data.name,
                )
                msg = "Department with this name already exists"
                raise ConflictException(msg)
            department.name = department_data.name

        if department_data.description is not None:
            department.description = department_data.description

        department.updated_at = datetime.now(UTC)

        updated = await self._uow.departments.update(department)
        logger.info("Department updated (department_id={})", updated.id)
        return updated

    async def delete_department(self, department_id: int) -> None:
        """Delete department."""
        logger.debug("Deleting department (department_id={})", department_id)
        department = await self.get_department_by_id(department_id)

        has_users = await self._uow.departments.has_users(department_id)
        if has_users:
            logger.warning(
                "Cannot delete department with assigned users (department_id={}, name={})",
                department_id,
                department.name,
            )
            msg = "Cannot delete department with assigned users"
            raise ConflictException(msg)

        deleted = await self._uow.departments.delete(department_id)
        if not deleted:
            logger.warning("Delete department: not found (department_id={})", department_id)
            msg = "Department"
            raise NotFoundException(msg)
        await self._uow.commit()
        logger.info("Department deleted (department_id={})", department_id)
