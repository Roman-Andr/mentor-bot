"""Unit tests for internal API endpoints."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from meeting_service.api import deps
from meeting_service.api.internal import router as internal_router


def create_internal_test_app(mock_uow: Any) -> FastAPI:
    """Create test app with dependency overrides for internal endpoints."""
    app = FastAPI()

    async def override_uow() -> Any:
        try:
            yield mock_uow
        finally:
            pass

    app.dependency_overrides[deps.get_uow] = override_uow
    app.dependency_overrides[deps.verify_service_api_key] = lambda: True

    app.include_router(internal_router, prefix="/api/v1/meetings/internal")
    return app


class TestCleanupUserMeetingData:
    """Tests for DELETE /api/v1/meetings/internal/users/{user_id} endpoint."""

    @pytest.mark.asyncio
    async def test_cleanup_user_data_success(self, mock_uow):
        """Test successful cleanup of user meeting data."""
        # Arrange
        mock_result = MagicMock()
        mock_result.rowcount = 2

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_uow._session = mock_session
        mock_uow.commit = AsyncMock()

        app = create_internal_test_app(mock_uow)
        client = TestClient(app)

        # Act
        response = client.delete(
            "/api/v1/meetings/internal/users/42",
            headers={"X-Service-Api-Key": "test-service-api-key"},
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "calendar_accounts" in data
        assert "user_meetings" in data
        assert "participant_history" in data
        assert "status_history" in data
        mock_uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_cleanup_user_data_returns_rowcounts(self, mock_uow):
        """Test that cleanup returns correct rowcounts."""
        # Arrange
        results = [MagicMock(rowcount=1), MagicMock(rowcount=3), MagicMock(rowcount=2), MagicMock(rowcount=0)]
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(side_effect=results)
        mock_uow._session = mock_session
        mock_uow.commit = AsyncMock()

        app = create_internal_test_app(mock_uow)
        client = TestClient(app)

        # Act
        response = client.delete(
            "/api/v1/meetings/internal/users/99",
            headers={"X-Service-Api-Key": "test-service-api-key"},
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["calendar_accounts"] == 1
        assert data["user_meetings"] == 3
        assert data["participant_history"] == 2
        assert data["status_history"] == 0

    @pytest.mark.asyncio
    async def test_cleanup_user_data_none_rowcount(self, mock_uow):
        """Test that None rowcount is treated as 0."""
        # Arrange
        mock_result = MagicMock()
        mock_result.rowcount = None

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_uow._session = mock_session
        mock_uow.commit = AsyncMock()

        app = create_internal_test_app(mock_uow)
        client = TestClient(app)

        # Act
        response = client.delete(
            "/api/v1/meetings/internal/users/10",
            headers={"X-Service-Api-Key": "test-service-api-key"},
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["calendar_accounts"] == 0
        assert data["user_meetings"] == 0

    @pytest.mark.asyncio
    async def test_cleanup_user_data_session_none_raises(self, mock_uow):
        """Test that missing session raises RuntimeError (500)."""
        # Arrange
        mock_uow._session = None

        app = create_internal_test_app(mock_uow)
        client = TestClient(app, raise_server_exceptions=False)

        # Act
        response = client.delete(
            "/api/v1/meetings/internal/users/42",
            headers={"X-Service-Api-Key": "test-service-api-key"},
        )

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
