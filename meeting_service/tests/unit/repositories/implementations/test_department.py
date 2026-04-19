"""Unit tests for Department repository implementation."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from meeting_service.models import Department
from meeting_service.repositories.implementations.department import DepartmentRepository


class TestDepartmentRepositoryGetByName:
    """Tests for DepartmentRepository.get_by_name method (lines 20-22 coverage)."""

    @pytest.mark.asyncio
    async def test_get_by_name_returns_department(self):
        """Test getting a department by name when it exists."""
        # Arrange
        mock_session = MagicMock(spec=AsyncSession)
        mock_result = MagicMock()
        expected_dept = Department(id=1, name="Engineering", description="Software engineering")
        mock_result.scalar_one_or_none.return_value = expected_dept
        mock_session.execute = AsyncMock(return_value=mock_result)

        repo = DepartmentRepository(mock_session)

        # Act
        result = await repo.get_by_name("Engineering")

        # Assert
        assert result == expected_dept
        assert result.name == "Engineering"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_name_returns_none_when_not_found(self):
        """Test getting a department by name when it doesn't exist."""
        # Arrange
        mock_session = MagicMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        repo = DepartmentRepository(mock_session)

        # Act
        result = await repo.get_by_name("NonExistent")

        # Assert
        assert result is None
        mock_session.execute.assert_called_once()
