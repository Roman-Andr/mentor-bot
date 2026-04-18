"""Tests for department API endpoints.

Covers:
- Lines 20-38: create_department endpoint
- Lines 48-58: get_department endpoint
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, status
from sqlalchemy import select

from knowledge_service.api.endpoints.departments import (
    create_department,
    get_department,
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
            if hasattr(obj, 'id') and obj.id is None:
                obj.id = 1
            if not hasattr(obj, 'created_at') or obj.created_at is None:
                obj.created_at = datetime.now(UTC)
            if not hasattr(obj, 'updated_at') or obj.updated_at is None:
                obj.updated_at = datetime.now(UTC)

        mock_session.refresh = mock_refresh

        with patch("knowledge_service.database.AsyncSessionLocal") as mock_session_class:
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

        with patch("knowledge_service.database.AsyncSessionLocal") as mock_session_class:
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

        with patch("knowledge_service.database.AsyncSessionLocal") as mock_session_class:
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

        with patch("knowledge_service.database.AsyncSessionLocal") as mock_session_class:
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
