"""Unit tests for departments API endpoints."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, status

from checklists_service.api.endpoints import departments
from checklists_service.models.department import Department
from checklists_service.schemas import DepartmentCreate


class TestCreateDepartment:
    """Test POST /departments endpoint."""

    async def test_create_department_success(self) -> None:
        """Test successful department creation."""
        dept_data = DepartmentCreate(name="Engineering", description="Engineering Team")

        # Create a mock result for scalar_one_or_none (None = no existing)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        # Mock the database session
        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Mock AsyncSessionLocal to return our mock session
        with patch(
            "checklists_service.api.endpoints.departments.AsyncSessionLocal"
        ) as mock_session_class:
            mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=False)

            # Mock the department creation - when add is called, set the id
            def mock_add(dept) -> None:
                dept.id = 1
                dept.created_at = datetime.now(UTC)

            mock_session.add.side_effect = mock_add

            # Mock service and auth (passed as dependencies)
            mock_service = MagicMock()
            mock_auth = True

            result = await departments.create_department(dept_data, mock_service, mock_auth)

            assert result.name == "Engineering"
            assert result.description == "Engineering Team"

    async def test_create_department_already_exists(self) -> None:
        """Test department creation fails when name already exists."""
        dept_data = DepartmentCreate(name="Engineering", description="Engineering Team")

        # Create existing department
        existing_dept = Department(
            id=1,
            name="Engineering",
            description="Existing Engineering",
            created_at=datetime.now(UTC),
            updated_at=None,
        )

        # Create a mock result that returns the existing department
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_dept

        # Mock the database session
        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result

        with patch(
            "checklists_service.api.endpoints.departments.AsyncSessionLocal"
        ) as mock_session_class:
            mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_service = MagicMock()
            mock_auth = True

            with pytest.raises(HTTPException) as exc_info:
                await departments.create_department(dept_data, mock_service, mock_auth)

            assert exc_info.value.status_code == status.HTTP_409_CONFLICT
            assert "already exists" in exc_info.value.detail.lower()


class TestGetDepartment:
    """Test GET /departments/{department_name} endpoint."""

    async def test_get_department_success(self) -> None:
        """Test successful department retrieval."""
        # Create existing department
        existing_dept = Department(
            id=1,
            name="Engineering",
            description="Engineering Team",
            created_at=datetime.now(UTC),
            updated_at=None,
        )

        # Create a mock result that returns the department
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_dept

        # Mock the database session
        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result

        with patch(
            "checklists_service.api.endpoints.departments.AsyncSessionLocal"
        ) as mock_session_class:
            mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_service = MagicMock()
            mock_auth = True

            result = await departments.get_department("Engineering", mock_service, mock_auth)

            assert result.name == "Engineering"
            assert result.description == "Engineering Team"

    async def test_get_department_not_found(self) -> None:
        """Test department retrieval returns 404 when not found."""
        # Create a mock result that returns None
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        # Mock the database session
        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result

        with patch(
            "checklists_service.api.endpoints.departments.AsyncSessionLocal"
        ) as mock_session_class:
            mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_service = MagicMock()
            mock_auth = True

            with pytest.raises(HTTPException) as exc_info:
                await departments.get_department("NonExistent", mock_service, mock_auth)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert "not found" in exc_info.value.detail.lower()


class TestUpdateDepartment:
    """Test PUT /departments/{department_name} endpoint (lines 62-83)."""

    async def test_update_department_success_same_name(self) -> None:
        """Test successful department update with same name (lines 62-83)."""
        from datetime import UTC, datetime

        existing_dept = Department(
            id=1,
            name="Engineering",
            description="Engineering Team",
            created_at=datetime.now(UTC),
            updated_at=None,
        )

        dept_data = DepartmentCreate(name="Engineering", description="Updated Engineering Team")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_dept

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch(
            "checklists_service.api.endpoints.departments.AsyncSessionLocal"
        ) as mock_session_class:
            mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_service = MagicMock()
            mock_auth = True

            result = await departments.update_department("Engineering", dept_data, mock_service, mock_auth)

            assert result.name == "Engineering"
            assert result.description == "Updated Engineering Team"
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once()

    async def test_update_department_success_rename(self) -> None:
        """Test successful department update with name change (lines 68-76)."""
        from datetime import UTC, datetime

        existing_dept = Department(
            id=1,
            name="Engineering",
            description="Engineering Team",
            created_at=datetime.now(UTC),
            updated_at=None,
        )

        dept_data = DepartmentCreate(name="NewEngineering", description="Updated Team")

        # First execute finds the existing dept
        mock_result1 = MagicMock()
        mock_result1.scalar_one_or_none.return_value = existing_dept

        # Second execute checks for name conflict (returns None = no conflict)
        mock_result2 = MagicMock()
        mock_result2.scalar_one_or_none.return_value = None

        mock_session = AsyncMock()
        mock_session.execute.side_effect = [mock_result1, mock_result2]
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch(
            "checklists_service.api.endpoints.departments.AsyncSessionLocal"
        ) as mock_session_class:
            mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_service = MagicMock()
            mock_auth = True

            result = await departments.update_department("Engineering", dept_data, mock_service, mock_auth)

            assert result.name == "NewEngineering"
            assert result.description == "Updated Team"
            assert existing_dept.name == "NewEngineering"
            mock_session.commit.assert_called_once()

    async def test_update_department_not_found(self) -> None:
        """Test department update returns 404 when not found (lines 64-66)."""
        dept_data = DepartmentCreate(name="NewName", description="New Description")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result

        with patch(
            "checklists_service.api.endpoints.departments.AsyncSessionLocal"
        ) as mock_session_class:
            mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_service = MagicMock()
            mock_auth = True

            with pytest.raises(HTTPException) as exc_info:
                await departments.update_department("NonExistent", dept_data, mock_service, mock_auth)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert "not found" in exc_info.value.detail.lower()

    async def test_update_department_name_conflict(self) -> None:
        """Test department update returns 409 when new name already exists (lines 69-75)."""
        from datetime import UTC, datetime

        existing_dept = Department(
            id=1,
            name="Engineering",
            description="Engineering Team",
            created_at=datetime.now(UTC),
            updated_at=None,
        )

        conflicting_dept = Department(
            id=2,
            name="NewEngineering",
            description="Another Team",
            created_at=datetime.now(UTC),
            updated_at=None,
        )

        dept_data = DepartmentCreate(name="NewEngineering", description="Updated Team")

        # First execute finds the existing dept
        mock_result1 = MagicMock()
        mock_result1.scalar_one_or_none.return_value = existing_dept

        # Second execute finds a conflict
        mock_result2 = MagicMock()
        mock_result2.scalar_one_or_none.return_value = conflicting_dept

        mock_session = AsyncMock()
        mock_session.execute.side_effect = [mock_result1, mock_result2]

        with patch(
            "checklists_service.api.endpoints.departments.AsyncSessionLocal"
        ) as mock_session_class:
            mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_service = MagicMock()
            mock_auth = True

            with pytest.raises(HTTPException) as exc_info:
                await departments.update_department("Engineering", dept_data, mock_service, mock_auth)

            assert exc_info.value.status_code == status.HTTP_409_CONFLICT
            assert "already exists" in exc_info.value.detail.lower()

    async def test_update_department_only_description(self) -> None:
        """Test update only description when name is unchanged (lines 78-79)."""
        from datetime import UTC, datetime

        existing_dept = Department(
            id=1,
            name="Engineering",
            description="Old Description",
            created_at=datetime.now(UTC),
            updated_at=None,
        )

        # Only update description
        dept_data = DepartmentCreate(name="Engineering", description="New Description")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_dept

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch(
            "checklists_service.api.endpoints.departments.AsyncSessionLocal"
        ) as mock_session_class:
            mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_service = MagicMock()
            mock_auth = True

            result = await departments.update_department("Engineering", dept_data, mock_service, mock_auth)

            assert result.description == "New Description"
            mock_session.commit.assert_called_once()

    async def test_update_department_description_none(self) -> None:
        """Test that description is not updated when data.description is None (lines 78-79)."""
        from datetime import UTC, datetime

        existing_dept = Department(
            id=1,
            name="Engineering",
            description="Original Description",
            created_at=datetime.now(UTC),
            updated_at=None,
        )

        # Update name but description is None - should not change existing description
        dept_data = DepartmentCreate(name="NewEngineering", description=None)

        mock_result1 = MagicMock()
        mock_result1.scalar_one_or_none.return_value = existing_dept

        mock_result2 = MagicMock()
        mock_result2.scalar_one_or_none.return_value = None  # No conflict

        mock_session = AsyncMock()
        mock_session.execute.side_effect = [mock_result1, mock_result2]
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch(
            "checklists_service.api.endpoints.departments.AsyncSessionLocal"
        ) as mock_session_class:
            mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_service = MagicMock()
            mock_auth = True

            result = await departments.update_department("Engineering", dept_data, mock_service, mock_auth)

            # Description should remain unchanged since data.description is None
            assert existing_dept.description == "Original Description"
            mock_session.commit.assert_called_once()


class TestDeleteDepartment:
    """Test DELETE /departments/{department_name} endpoint."""

    async def test_delete_department_success(self) -> None:
        """Test successful department deletion."""
        # Create existing department
        existing_dept = Department(
            id=1,
            name="Engineering",
            description="Engineering Team",
            created_at=datetime.now(UTC),
            updated_at=None,
        )

        # Create a mock result that returns the department
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_dept

        # Mock the database session
        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_session.delete = AsyncMock()
        mock_session.commit = AsyncMock()

        with patch(
            "checklists_service.api.endpoints.departments.AsyncSessionLocal"
        ) as mock_session_class:
            mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_service = MagicMock()
            mock_auth = True

            result = await departments.delete_department("Engineering", mock_service, mock_auth)

            assert "deleted" in result.message.lower() or "success" in result.message.lower()
            mock_session.delete.assert_called_once_with(existing_dept)
            mock_session.commit.assert_called_once()

    async def test_delete_department_not_found(self) -> None:
        """Test department deletion returns 404 when not found."""
        # Create a mock result that returns None
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        # Mock the database session
        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result

        with patch(
            "checklists_service.api.endpoints.departments.AsyncSessionLocal"
        ) as mock_session_class:
            mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_service = MagicMock()
            mock_auth = True

            with pytest.raises(HTTPException) as exc_info:
                await departments.delete_department("NonExistent", mock_service, mock_auth)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert "not found" in exc_info.value.detail.lower()
