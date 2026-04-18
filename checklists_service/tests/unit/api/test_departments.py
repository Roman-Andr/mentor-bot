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
            "checklists_service.database.AsyncSessionLocal"
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
            "checklists_service.database.AsyncSessionLocal"
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
            "checklists_service.database.AsyncSessionLocal"
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
            "checklists_service.database.AsyncSessionLocal"
        ) as mock_session_class:
            mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_service = MagicMock()
            mock_auth = True

            with pytest.raises(HTTPException) as exc_info:
                await departments.get_department("NonExistent", mock_service, mock_auth)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert "not found" in exc_info.value.detail.lower()


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
            "checklists_service.database.AsyncSessionLocal"
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
            "checklists_service.database.AsyncSessionLocal"
        ) as mock_session_class:
            mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_service = MagicMock()
            mock_auth = True

            with pytest.raises(HTTPException) as exc_info:
                await departments.delete_department("NonExistent", mock_service, mock_auth)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert "not found" in exc_info.value.detail.lower()
