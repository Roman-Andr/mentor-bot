"""Unit tests for auth_service/services/user_cleanup.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from auth_service.services.user_cleanup import UserCleanupClient


class TestUserCleanupClient:
    async def test_cleanup_user_data_success(self) -> None:
        """Calls all cleanup endpoints successfully."""
        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.delete = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("auth_service.services.user_cleanup.httpx.AsyncClient", return_value=mock_client):
            client = UserCleanupClient()
            await client.cleanup_user_data(42)

        assert mock_client.delete.await_count == len(client._targets)

    async def test_cleanup_raises_on_error_response(self) -> None:
        """Raises HTTPStatusError when a service returns 4xx/5xx."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500", request=MagicMock(), response=mock_response
        )

        mock_client = AsyncMock()
        mock_client.delete = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("auth_service.services.user_cleanup.httpx.AsyncClient", return_value=mock_client):
            client = UserCleanupClient()
            with pytest.raises(httpx.HTTPStatusError):
                await client.cleanup_user_data(99)
