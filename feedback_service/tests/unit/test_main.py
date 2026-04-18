"""Unit tests for main.py endpoints."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from feedback_service.main import app, lifespan

client = TestClient(app)


class TestLifespan:
    """Tests for lifespan context manager (startup/shutdown)."""

    @pytest.mark.asyncio
    async def test_lifespan_initializes_database_on_startup(self) -> None:
        """Test lifespan calls init_db during startup."""
        # Arrange
        mock_app = MagicMock()

        with patch("feedback_service.main.init_db") as mock_init_db:
            mock_init_db.return_value = AsyncMock()

            # Act
            async with lifespan(mock_app):
                # During context - startup should have run
                mock_init_db.assert_called_once()

            # After exiting context - shutdown logging happens

    @pytest.mark.asyncio
    async def test_lifespan_handles_init_db_failure(self) -> None:
        """Test lifespan propagates database initialization errors."""
        # Arrange
        mock_app = MagicMock()

        with patch("feedback_service.main.init_db") as mock_init_db:
            from sqlalchemy.exc import SQLAlchemyError
            mock_init_db.side_effect = SQLAlchemyError("Database connection failed")

            # Act & Assert
            with pytest.raises(SQLAlchemyError, match="Database connection failed"):
                async with lifespan(mock_app):
                    pass  # Should not reach here

    @pytest.mark.asyncio
    async def test_lifespan_logs_shutdown(self) -> None:
        """Test lifespan logs shutdown message."""
        # Arrange
        mock_app = MagicMock()

        with patch("feedback_service.main.init_db") as mock_init_db, \
             patch("feedback_service.main.logger") as mock_logger:
            mock_init_db.return_value = AsyncMock()

            # Act
            async with lifespan(mock_app):
                pass  # Normal execution

            # Assert - shutdown was logged
            mock_logger.info.assert_any_call("Shutting down Feedback Service...")


class TestRootEndpoint:
    """Tests for GET / endpoint."""

    def test_root_returns_service_status(self) -> None:
        """Test root endpoint returns service status."""
        with patch("feedback_service.main.init_db", new_callable=AsyncMock):
            response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Feedback Service"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
        assert "docs" in data


class TestHealthEndpoint:
    """Tests for GET /health endpoint."""

    def test_health_check_returns_healthy(self) -> None:
        """Test health check returns healthy status."""
        # Mock engine.connect() for the health check test
        with patch("feedback_service.main.engine") as mock_engine:
            mock_conn = AsyncMock()
            mock_conn.execute = AsyncMock()

            class AsyncContextMock:
                async def __aenter__(self):
                    return mock_conn
                async def __aexit__(self, *args):
                    return False

            mock_engine.connect = MagicMock(return_value=AsyncContextMock())

            response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "feedback"
        assert "timestamp" in data
        assert "dependencies" in data
        assert data["dependencies"]["database"] == "connected"
        assert data["dependencies"]["auth_service"] == "enabled"

    def test_health_check_returns_unhealthy_when_db_disconnected(self) -> None:
        """Test health check returns unhealthy when database is disconnected."""
        # Mock engine.connect() to raise an exception
        with patch("feedback_service.main.engine") as mock_engine:

            class AsyncContextMock:
                async def __aenter__(self):
                    raise Exception("Database connection failed")
                async def __aexit__(self, *args):
                    return False

            mock_engine.connect = MagicMock(return_value=AsyncContextMock())

            response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["dependencies"]["database"] == "disconnected"
