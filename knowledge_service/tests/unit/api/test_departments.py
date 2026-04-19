"""
Tests for department API endpoints.

Covers:
- Lines 20-38: create_department endpoint
- Lines 48-58: get_department endpoint
- Lines 62-83: update_department endpoint
- Lines 93-101: delete_department endpoint
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, status

from knowledge_service.api.endpoints.departments import (
    create_department,
    delete_department,
    get_department,
    update_department,
)
from knowledge_service.models.department import Department
from knowledge_service.schemas.department import DepartmentCreate

if TYPE_CHECKING:
    from unittest.mock import AsyncMock


class TestCreateDepartment:
    """Test POST /departments endpoint - covers lines 20-38."""

    @pytest.fixture
    def mock_knowledge_service(self):
        """Create a mock knowledge service."""
        return AsyncMock()

    @pytest.fixture
    def mock_service_auth(self):
        """Create a mock service auth."""
        return MagicMock()

    async def test_create_department_success(
        self,
        mock_knowledge_service: AsyncMock,
        mock_service_auth: MagicMock,
    ) -> None:
        """Test successful department creation - covers lines 34-38."""
        department_data = DepartmentCreate(
            name="Engineering",
            description="Engineering Department",
        )

        # Create a real department model instance for the test
        mock_dept = Department(
            name="Engineering",
            description="Engineering Department",
        )
        mock_dept.id = 1
        mock_dept.created_at = datetime.now(UTC)
        mock_dept.updated_at = datetime.now(UTC)

        # Mock result for no existing department
        mock_result_no_existing = MagicMock()
        mock_result_no_existing.scalar_one_or_none.return_value = None

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result_no_existing)
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()

        # The refresh needs to actually set the id on the department object
        async def mock_refresh(obj):
            if hasattr(obj, "id") and obj.id is None:
                obj.id = 1
            if not hasattr(obj, "created_at") or obj.created_at is None:
                obj.created_at = datetime.now(UTC)
            if not hasattr(obj, "updated_at") or obj.updated_at is None:
                obj.updated_at = datetime.now(UTC)

        mock_session.refresh = mock_refresh

        with patch("knowledge_service.api.endpoints.departments.AsyncSessionLocal") as mock_session_class:
            mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=False)

            result = await create_department(
                department_data=department_data,
                _service=mock_knowledge_service,
                _auth=mock_service_auth,
            )

            assert result.name == "Engineering"
            assert result.description == "Engineering Department"

    async def test_create_department_duplicate(
        self,
        mock_knowledge_service: AsyncMock,
        mock_service_auth: MagicMock,
    ) -> None:
        """Test department creation with duplicate name - covers lines 20-32."""
        department_data = DepartmentCreate(
            name="Engineering",
            description="Engineering Department",
        )

        # Mock existing department
        mock_existing = MagicMock()
        mock_existing.id = 1
        mock_existing.name = "Engineering"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_existing

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch("knowledge_service.api.endpoints.departments.AsyncSessionLocal") as mock_session_class:
            mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=False)

            with pytest.raises(HTTPException) as exc_info:
                await create_department(
                    department_data=department_data,
                    _service=mock_knowledge_service,
                    _auth=mock_service_auth,
                )

            assert exc_info.value.status_code == status.HTTP_409_CONFLICT
            assert "already exists" in exc_info.value.detail


class TestGetDepartment:
    """Test GET /departments/{name} endpoint - covers lines 48-58."""

    @pytest.fixture
    def mock_knowledge_service(self):
        """Create a mock knowledge service."""
        return AsyncMock()

    @pytest.fixture
    def mock_service_auth(self):
        """Create a mock service auth."""
        return MagicMock()

    async def test_get_department_success(
        self,
        mock_knowledge_service: AsyncMock,
        mock_service_auth: MagicMock,
    ) -> None:
        """Test successful department retrieval - covers lines 48-58."""
        # Mock existing department
        mock_dept = MagicMock()
        mock_dept.id = 1
        mock_dept.name = "Engineering"
        mock_dept.description = "Engineering Department"
        mock_dept.created_at = datetime.now(UTC)
        mock_dept.updated_at = datetime.now(UTC)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_dept

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch("knowledge_service.api.endpoints.departments.AsyncSessionLocal") as mock_session_class:
            mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=False)

            result = await get_department(
                department_name="Engineering",
                _service=mock_knowledge_service,
                _auth=mock_service_auth,
            )

            assert result.name == "Engineering"
            assert result.description == "Engineering Department"

    async def test_get_department_not_found(
        self,
        mock_knowledge_service: AsyncMock,
        mock_service_auth: MagicMock,
    ) -> None:
        """Test department retrieval when not found - covers 404 case."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch("knowledge_service.api.endpoints.departments.AsyncSessionLocal") as mock_session_class:
            mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=False)

            with pytest.raises(HTTPException) as exc_info:
                await get_department(
                    department_name="NonExistent",
                    _service=mock_knowledge_service,
                    _auth=mock_service_auth,
                )

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert "not found" in exc_info.value.detail


class TestUpdateDepartment:
    """Test PUT /departments/{name} endpoint - covers lines 62-83."""

    @pytest.fixture
    def mock_knowledge_service(self):
        """Create a mock knowledge service."""
        return AsyncMock()

    @pytest.fixture
    def mock_service_auth(self):
        """Create a mock service auth."""
        return MagicMock()

    async def test_update_department_success(
        self,
        mock_knowledge_service: AsyncMock,
        mock_service_auth: MagicMock,
    ) -> None:
        """Test successful department update - covers lines 62-83."""
        department_data = DepartmentCreate(
            name="Updated Engineering",
            description="Updated Engineering Department",
        )

        # Mock existing department
        mock_dept = MagicMock()
        mock_dept.id = 1
        mock_dept.name = "Engineering"
        mock_dept.description = "Engineering Department"
        mock_dept.created_at = datetime.now(UTC)
        mock_dept.updated_at = datetime.now(UTC)

        # First result for finding the department to update
        mock_result_find = MagicMock()
        mock_result_find.scalar_one_or_none.return_value = mock_dept

        # Second result for checking if new name already exists (should be None)
        mock_result_check = MagicMock()
        mock_result_check.scalar_one_or_none.return_value = None

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(side_effect=[mock_result_find, mock_result_check])
        mock_session.commit = AsyncMock()

        async def mock_refresh(obj):
            if hasattr(obj, "updated_at"):
                obj.updated_at = datetime.now(UTC)

        mock_session.refresh = mock_refresh

        with patch("knowledge_service.api.endpoints.departments.AsyncSessionLocal") as mock_session_class:
            mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=False)

            result = await update_department(
                department_name="Engineering",
                department_data=department_data,
                _service=mock_knowledge_service,
                _auth=mock_service_auth,
            )

            assert result.name == "Updated Engineering"
            assert result.description == "Updated Engineering Department"

    async def test_update_department_not_found(
        self,
        mock_knowledge_service: AsyncMock,
        mock_service_auth: MagicMock,
    ) -> None:
        """Test update when department not found - covers 404 case."""
        department_data = DepartmentCreate(
            name="Updated Engineering",
            description="Updated Engineering Department",
        )

        # First result - department not found
        mock_result_find = MagicMock()
        mock_result_find.scalar_one_or_none.return_value = None

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result_find)

        with patch("knowledge_service.api.endpoints.departments.AsyncSessionLocal") as mock_session_class:
            mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=False)

            with pytest.raises(HTTPException) as exc_info:
                await update_department(
                    department_name="NonExistent",
                    department_data=department_data,
                    _service=mock_knowledge_service,
                    _auth=mock_service_auth,
                )

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert "not found" in exc_info.value.detail

    async def test_update_department_duplicate_name(
        self,
        mock_knowledge_service: AsyncMock,
        mock_service_auth: MagicMock,
    ) -> None:
        """Test update with duplicate name - covers 409 conflict case."""
        department_data = DepartmentCreate(
            name="Existing Department",
            description="Updated description",
        )

        # Mock existing department to update
        mock_dept = MagicMock()
        mock_dept.id = 1
        mock_dept.name = "Engineering"
        mock_dept.description = "Engineering Department"

        # Another department with the target name already exists
        mock_existing = MagicMock()
        mock_existing.id = 2
        mock_existing.name = "Existing Department"

        # First result for finding the department to update
        mock_result_find = MagicMock()
        mock_result_find.scalar_one_or_none.return_value = mock_dept

        # Second result - checking if new name exists - returns existing department
        mock_result_check = MagicMock()
        mock_result_check.scalar_one_or_none.return_value = mock_existing

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(side_effect=[mock_result_find, mock_result_check])

        with patch("knowledge_service.api.endpoints.departments.AsyncSessionLocal") as mock_session_class:
            mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=False)

            with pytest.raises(HTTPException) as exc_info:
                await update_department(
                    department_name="Engineering",
                    department_data=department_data,
                    _service=mock_knowledge_service,
                    _auth=mock_service_auth,
                )

            assert exc_info.value.status_code == status.HTTP_409_CONFLICT
            assert "already exists" in exc_info.value.detail

    async def test_update_department_same_name_no_conflict_check(
        self,
        mock_knowledge_service: AsyncMock,
        mock_service_auth: MagicMock,
    ) -> None:
        """Test update when name doesn't change - no conflict check needed."""
        department_data = DepartmentCreate(
            name="Engineering",  # Same name as existing
            description="Updated Engineering Department",
        )

        # Mock existing department
        mock_dept = MagicMock()
        mock_dept.id = 1
        mock_dept.name = "Engineering"
        mock_dept.description = "Engineering Department"
        mock_dept.created_at = datetime.now(UTC)
        mock_dept.updated_at = datetime.now(UTC)

        # Only one execute call since name doesn't change
        mock_result_find = MagicMock()
        mock_result_find.scalar_one_or_none.return_value = mock_dept

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result_find)
        mock_session.commit = AsyncMock()

        async def mock_refresh(obj):
            if hasattr(obj, "updated_at"):
                obj.updated_at = datetime.now(UTC)

        mock_session.refresh = mock_refresh

        with patch("knowledge_service.api.endpoints.departments.AsyncSessionLocal") as mock_session_class:
            mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=False)

            result = await update_department(
                department_name="Engineering",
                department_data=department_data,
                _service=mock_knowledge_service,
                _auth=mock_service_auth,
            )

            assert result.name == "Engineering"
            assert result.description == "Updated Engineering Department"
            # Verify only one execute was called (no conflict check)
            assert mock_session.execute.call_count == 1

    async def test_update_department_description_only(
        self,
        mock_knowledge_service: AsyncMock,
        mock_service_auth: MagicMock,
    ) -> None:
        """Test update with description only (None name update)."""
        department_data = DepartmentCreate(
            name="Engineering",  # Same name
            description=None,  # Setting description to None
        )

        # Mock existing department
        mock_dept = MagicMock()
        mock_dept.id = 1
        mock_dept.name = "Engineering"
        mock_dept.description = "Old description"
        mock_dept.created_at = datetime.now(UTC)
        mock_dept.updated_at = datetime.now(UTC)

        mock_result_find = MagicMock()
        mock_result_find.scalar_one_or_none.return_value = mock_dept

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result_find)
        mock_session.commit = AsyncMock()

        async def mock_refresh(obj):
            if hasattr(obj, "updated_at"):
                obj.updated_at = datetime.now(UTC)

        mock_session.refresh = mock_refresh

        with patch("knowledge_service.api.endpoints.departments.AsyncSessionLocal") as mock_session_class:
            mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=False)

            result = await update_department(
                department_name="Engineering",
                department_data=department_data,
                _service=mock_knowledge_service,
                _auth=mock_service_auth,
            )

            assert result.name == "Engineering"


class TestDeleteDepartment:
    """Test DELETE /departments/{name} endpoint - covers lines 93-101."""

    @pytest.fixture
    def mock_knowledge_service(self):
        """Create a mock knowledge service."""
        return AsyncMock()

    @pytest.fixture
    def mock_service_auth(self):
        """Create a mock service auth."""
        return MagicMock()

    async def test_delete_department_success(
        self,
        mock_knowledge_service: AsyncMock,
        mock_service_auth: MagicMock,
    ) -> None:
        """Test successful department deletion - covers lines 93-101."""
        # Mock existing department
        mock_dept = MagicMock()
        mock_dept.id = 1
        mock_dept.name = "Engineering"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_dept

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.delete = AsyncMock()
        mock_session.commit = AsyncMock()

        with patch("knowledge_service.api.endpoints.departments.AsyncSessionLocal") as mock_session_class:
            mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=False)

            result = await delete_department(
                department_name="Engineering",
                _service=mock_knowledge_service,
                _auth=mock_service_auth,
            )

            assert result["message"] == "Department deleted successfully"
            mock_session.delete.assert_called_once_with(mock_dept)
            mock_session.commit.assert_called_once()

    async def test_delete_department_not_found(
        self,
        mock_knowledge_service: AsyncMock,
        mock_service_auth: MagicMock,
    ) -> None:
        """Test delete when department not found - covers 404 case."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch("knowledge_service.api.endpoints.departments.AsyncSessionLocal") as mock_session_class:
            mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=False)

            with pytest.raises(HTTPException) as exc_info:
                await delete_department(
                    department_name="NonExistent",
                    _service=mock_knowledge_service,
                    _auth=mock_service_auth,
                )

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert "not found" in exc_info.value.detail
