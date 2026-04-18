"""Unit tests for department_sync client."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from auth_service.utils.department_sync import DepartmentSyncClient


class TestDepartmentSyncClientInit:
    """Tests for DepartmentSyncClient initialization."""

    def test_init_creates_client(self):
        """Test that __init__ creates an httpx client."""
        client = DepartmentSyncClient()
        assert isinstance(client._client, httpx.AsyncClient)
        assert client._client.timeout.read == 30.0

    def test_init_sets_headers(self):
        """Test that __init__ sets the service API key header."""
        with patch("auth_service.utils.department_sync.settings") as mock_settings:
            mock_settings.SERVICE_API_KEY = "test-api-key"
            client = DepartmentSyncClient()
            assert client._headers == {"X-Service-Api-Key": "test-api-key"}


class TestDepartmentSyncClientClose:
    """Tests for DepartmentSyncClient.close method."""

    async def test_close_closes_client(self):
        """Test that close properly closes the httpx client."""
        client = DepartmentSyncClient()
        client._client.aclose = AsyncMock()

        await client.close()

        client._client.aclose.assert_awaited_once()


class TestCreateDepartmentInService:
    """Tests for create_department_in_service method."""

    @pytest.fixture
    def sync_client(self):
        """Create a DepartmentSyncClient with mocked client."""
        client = DepartmentSyncClient()
        client._client = MagicMock(spec=httpx.AsyncClient)
        return client

    async def test_create_success_200(self, sync_client):
        """Test successful creation with 200 response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        sync_client._client.post = AsyncMock(return_value=mock_response)

        result = await sync_client.create_department_in_service(
            "http://test-service", "Engineering", "Engineering Department"
        )

        assert result is True
        sync_client._client.post.assert_awaited_once_with(
            "http://test-service/api/v1/departments/",
            json={"name": "Engineering", "description": "Engineering Department"},
            headers=sync_client._headers,
        )

    async def test_create_success_201(self, sync_client):
        """Test successful creation with 201 response."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        sync_client._client.post = AsyncMock(return_value=mock_response)

        result = await sync_client.create_department_in_service(
            "http://test-service", "HR", "HR Department"
        )

        assert result is True

    async def test_create_already_exists_409(self, sync_client):
        """Test that 409 Conflict is treated as success (already exists)."""
        mock_response = MagicMock()
        mock_response.status_code = 409
        sync_client._client.post = AsyncMock(return_value=mock_response)

        result = await sync_client.create_department_in_service(
            "http://test-service", "Engineering", None
        )

        assert result is True

    async def test_create_failure_400(self, sync_client):
        """Test that 400 response returns False."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        sync_client._client.post = AsyncMock(return_value=mock_response)

        result = await sync_client.create_department_in_service(
            "http://test-service", "Engineering", None
        )

        assert result is False

    async def test_create_failure_500(self, sync_client):
        """Test that 500 response returns False."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        sync_client._client.post = AsyncMock(return_value=mock_response)

        result = await sync_client.create_department_in_service(
            "http://test-service", "Engineering", None
        )

        assert result is False

    async def test_create_request_error(self, sync_client):
        """Test that RequestError is caught and returns False."""
        sync_client._client.post = AsyncMock(side_effect=httpx.RequestError("Connection failed"))

        result = await sync_client.create_department_in_service(
            "http://test-service", "Engineering", None
        )

        assert result is False

    async def test_create_generic_exception(self, sync_client):
        """Test that generic exceptions are caught and return False."""
        sync_client._client.post = AsyncMock(side_effect=Exception("Unexpected error"))

        result = await sync_client.create_department_in_service(
            "http://test-service", "Engineering", None
        )

        assert result is False

    async def test_create_with_none_description(self, sync_client):
        """Test creation with None description."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        sync_client._client.post = AsyncMock(return_value=mock_response)

        result = await sync_client.create_department_in_service(
            "http://test-service", "Engineering", None
        )

        assert result is True
        sync_client._client.post.assert_awaited_once_with(
            "http://test-service/api/v1/departments/",
            json={"name": "Engineering", "description": None},
            headers=sync_client._headers,
        )


class TestSyncDepartment:
    """Tests for sync_department method."""

    @pytest.fixture
    def sync_client(self):
        """Create a DepartmentSyncClient."""
        client = DepartmentSyncClient()
        return client

    @pytest.fixture
    def mock_settings(self):
        """Mock settings with service URLs."""
        with patch("auth_service.utils.department_sync.settings") as settings:
            settings.CHECKLISTS_SERVICE_URL = "http://checklists:8002"
            settings.KNOWLEDGE_SERVICE_URL = "http://knowledge:8003"
            settings.MEETING_SERVICE_URL = "http://meeting:8006"
            yield settings

    async def test_sync_all_services_success(self, sync_client, mock_settings):
        """Test successful sync to all services."""
        with patch.object(
            sync_client, "create_department_in_service", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = True

            result = await sync_client.sync_department("Engineering", "Engineering Dept")

            assert result == {
                "checklists": True,
                "knowledge": True,
                "meeting": True,
            }
            assert mock_create.await_count == 3

    async def test_sync_partial_failure(self, sync_client, mock_settings):
        """Test sync when some services fail."""
        with patch.object(
            sync_client, "create_department_in_service", new_callable=AsyncMock
        ) as mock_create:
            mock_create.side_effect = [True, False, True]

            result = await sync_client.sync_department("Engineering", "Engineering Dept")

            assert result == {
                "checklists": True,
                "knowledge": False,
                "meeting": True,
            }

    async def test_sync_all_fail(self, sync_client, mock_settings):
        """Test sync when all services fail."""
        with patch.object(
            sync_client, "create_department_in_service", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = False

            result = await sync_client.sync_department("Engineering", "Engineering Dept")

            assert result == {
                "checklists": False,
                "knowledge": False,
                "meeting": False,
            }

    async def test_sync_with_none_description(self, sync_client, mock_settings):
        """Test sync with None description."""
        with patch.object(
            sync_client, "create_department_in_service", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = True

            result = await sync_client.sync_department("Engineering", None)

            assert result["checklists"] is True
            mock_create.assert_any_await("http://checklists:8002", "Engineering", None)


class TestDepartmentSyncClientSingleton:
    """Tests for the department_sync_client singleton."""

    def test_singleton_exists(self):
        """Test that the singleton instance exists."""
        from auth_service.utils.department_sync import department_sync_client

        assert isinstance(department_sync_client, DepartmentSyncClient)
