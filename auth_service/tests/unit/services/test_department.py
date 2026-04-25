"""Unit tests for department_service/services/department.py."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from auth_service.core import ConflictException, NotFoundException
from auth_service.models import Department
from auth_service.schemas import DepartmentCreate, DepartmentUpdate
from auth_service.services.department import DepartmentService


@pytest.fixture
def sample_department():
    """Create a sample department for testing."""
    return Department(
        id=1,
        name="Engineering",
        description="Software Engineering Department",
        created_at=datetime.now(UTC),
        updated_at=None,
    )


@pytest.fixture
def another_department():
    """Create another department for testing."""
    return Department(
        id=2,
        name="Marketing",
        description="Marketing and Sales Department",
        created_at=datetime.now(UTC),
        updated_at=None,
    )


class TestGetDepartmentById:
    """Tests for DepartmentService.get_department_by_id method."""

    async def test_get_department_by_id_success(self, mock_uow, sample_department):
        """Test getting department by ID returns department."""
        mock_uow.departments.get_by_id.return_value = sample_department
        service = DepartmentService(mock_uow)

        department = await service.get_department_by_id(1)

        assert department == sample_department
        mock_uow.departments.get_by_id.assert_called_once_with(1)

    async def test_get_department_by_id_not_found_raises(self, mock_uow):
        """Test getting non-existent department raises NotFoundException."""
        mock_uow.departments.get_by_id.return_value = None
        service = DepartmentService(mock_uow)

        with pytest.raises(NotFoundException) as exc_info:
            await service.get_department_by_id(999)

        assert "not found" in str(exc_info.value.detail).lower()


class TestGetDepartments:
    """Tests for DepartmentService.get_departments method."""

    async def test_get_departments_success(self, mock_uow, sample_department, another_department):
        """Test getting paginated list of departments."""
        departments = [sample_department, another_department]
        mock_uow.departments.find_departments.return_value = (departments, 2)
        service = DepartmentService(mock_uow)

        result, total = await service.get_departments(skip=0, limit=10)

        assert len(result) == 2
        assert total == 2
        mock_uow.departments.find_departments.assert_called_once()

    async def test_get_departments_with_search(self, mock_uow, sample_department):
        """Test getting departments with search filter."""
        mock_uow.departments.find_departments.return_value = ([sample_department], 1)
        service = DepartmentService(mock_uow)

        _result, _total = await service.get_departments(skip=0, limit=10, search="Engineering")

        mock_uow.departments.find_departments.assert_called_once_with(
            skip=0,
            limit=10,
            search="Engineering",
            sort_by=None,
            sort_order="asc",
        )

    async def test_get_departments_empty_list(self, mock_uow):
        """Test getting departments when none exist."""
        mock_uow.departments.find_departments.return_value = ([], 0)
        service = DepartmentService(mock_uow)

        result, total = await service.get_departments(skip=0, limit=10)

        assert len(result) == 0
        assert total == 0


class TestCreateDepartment:
    """Tests for DepartmentService.create_department method."""

    async def test_create_department_success(self, mock_uow, sample_department):
        """Test creating a new department."""
        mock_uow.departments.get_by_name.return_value = None
        mock_uow.departments.create.return_value = sample_department

        service = DepartmentService(mock_uow)
        department_data = DepartmentCreate(
            name="Engineering",
            description="Software Engineering Department",
        )

        department = await service.create_department(department_data)

        assert department.name == "Engineering"
        assert department.description == "Software Engineering Department"
        mock_uow.departments.create.assert_called_once()
        mock_uow.commit.assert_awaited_once()  # Verify transaction committed

    async def test_create_department_duplicate_name_raises(self, mock_uow, sample_department):
        """Test creating department with duplicate name raises ConflictException."""
        mock_uow.departments.get_by_name.return_value = sample_department
        service = DepartmentService(mock_uow)

        department_data = DepartmentCreate(
            name="Engineering",  # Already exists
            description="Another Engineering",
        )

        with pytest.raises(ConflictException) as exc_info:
            await service.create_department(department_data)

        assert "department with this name already exists" in str(exc_info.value.detail).lower()


class TestUpdateDepartment:
    """Tests for DepartmentService.update_department method."""

    async def test_update_department_success(self, mock_uow, sample_department):
        """Test updating department information."""
        mock_uow.departments.get_by_id.return_value = sample_department
        mock_uow.departments.get_by_name.return_value = None  # No name conflict

        updated = Department(
            id=sample_department.id,
            name="Updated Engineering",
            description="Updated Description",
            created_at=sample_department.created_at,
            updated_at=datetime.now(UTC),
        )
        mock_uow.departments.update.return_value = updated

        service = DepartmentService(mock_uow)
        department_data = DepartmentUpdate(
            name="Updated Engineering",
            description="Updated Description",
        )

        department = await service.update_department(1, department_data)

        assert department.name == "Updated Engineering"
        assert department.description == "Updated Description"
        mock_uow.departments.update.assert_called_once()

    async def test_update_department_not_found_raises(self, mock_uow):
        """Test updating non-existent department raises NotFoundException."""
        mock_uow.departments.get_by_id.return_value = None
        service = DepartmentService(mock_uow)

        department_data = DepartmentUpdate(name="New Name")

        with pytest.raises(NotFoundException) as exc_info:
            await service.update_department(999, department_data)

        assert "not found" in str(exc_info.value.detail).lower()

    async def test_update_department_duplicate_name_raises(self, mock_uow, sample_department, another_department):
        """Test updating to duplicate name raises ConflictException."""
        mock_uow.departments.get_by_id.return_value = sample_department
        mock_uow.departments.get_by_name.return_value = another_department  # Name conflict
        service = DepartmentService(mock_uow)

        department_data = DepartmentUpdate(name="Marketing")  # Another department name

        with pytest.raises(ConflictException) as exc_info:
            await service.update_department(1, department_data)

        assert "department with this name already exists" in str(exc_info.value.detail).lower()

    async def test_update_department_same_name_no_conflict(self, mock_uow, sample_department):
        """Test updating with same name (no change) does not raise conflict."""
        mock_uow.departments.get_by_id.return_value = sample_department
        # get_by_name is not called because name is the same

        updated = Department(
            id=sample_department.id,
            name="Engineering",  # Same name
            description="Updated Description",
            created_at=sample_department.created_at,
            updated_at=datetime.now(UTC),
        )
        mock_uow.departments.update.return_value = updated

        service = DepartmentService(mock_uow)
        department_data = DepartmentUpdate(
            name="Engineering",  # Same as current
            description="Updated Description",
        )

        department = await service.update_department(1, department_data)

        assert department.name == "Engineering"
        mock_uow.departments.get_by_name.assert_not_called()  # Should not check for conflict

    async def test_update_department_description_only(self, mock_uow, sample_department):
        """Test updating only description."""
        mock_uow.departments.get_by_id.return_value = sample_department

        updated = Department(
            id=sample_department.id,
            name="Engineering",  # Unchanged
            description="New Description",
            created_at=sample_department.created_at,
            updated_at=datetime.now(UTC),
        )
        mock_uow.departments.update.return_value = updated

        service = DepartmentService(mock_uow)
        department_data = DepartmentUpdate(description="New Description")

        department = await service.update_department(1, department_data)

        assert department.description == "New Description"
        assert department.name == "Engineering"


class TestDeleteDepartment:
    """Tests for DepartmentService.delete_department method."""

    async def test_delete_department_success(self, mock_uow, sample_department):
        """Test deleting a department."""
        mock_uow.departments.get_by_id.return_value = sample_department
        mock_uow.departments.has_users = AsyncMock(return_value=False)
        mock_uow.departments.delete.return_value = True
        service = DepartmentService(mock_uow)

        await service.delete_department(1)

        mock_uow.departments.delete.assert_called_once_with(1)

    async def test_delete_department_not_found_raises(self, mock_uow):
        """Test deleting non-existent department raises NotFoundException."""
        mock_uow.departments.get_by_id.return_value = None
        service = DepartmentService(mock_uow)

        with pytest.raises(NotFoundException) as exc_info:
            await service.delete_department(999)

        assert "not found" in str(exc_info.value.detail).lower()

    async def test_delete_department_with_users_raises(self, mock_uow, sample_department):
        """Test deleting department with assigned users raises ConflictException."""
        mock_uow.departments.get_by_id.return_value = sample_department
        mock_uow.departments.has_users = AsyncMock(return_value=True)
        service = DepartmentService(mock_uow)

        with pytest.raises(ConflictException) as exc_info:
            await service.delete_department(1)

        assert "cannot delete department with assigned users" in str(exc_info.value.detail).lower()
        mock_uow.departments.delete.assert_not_called()

    async def test_delete_department_returns_false_raises_not_found(self, mock_uow, sample_department):
        """Test delete returning False raises NotFoundException (covers lines 109-110)."""
        mock_uow.departments.get_by_id.return_value = sample_department
        mock_uow.departments.has_users = AsyncMock(return_value=False)
        mock_uow.departments.delete.return_value = False  # Delete returns False
        service = DepartmentService(mock_uow)

        with pytest.raises(NotFoundException) as exc_info:
            await service.delete_department(1)

        assert "not found" in str(exc_info.value.detail).lower()
        mock_uow.departments.delete.assert_called_once_with(1)
