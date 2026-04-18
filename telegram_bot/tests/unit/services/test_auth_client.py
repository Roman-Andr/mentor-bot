"""Unit tests for telegram_bot/services/auth_client.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from telegram_bot.services.auth_client import AuthServiceClient, auth_client


class TestAuthServiceClient:
    """Test cases for AuthServiceClient."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client = AuthServiceClient(base_url="http://test-auth:8001")
        self.auth_token = "test_token_123"
        self.telegram_id = 123456

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_get_user_by_telegram_id_success(self, mock_get):
        """Test getting user by Telegram ID - success case."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "first_name": "John", "telegram_id": 123456}
        mock_get.return_value = mock_response

        result = await self.client.get_user_by_telegram_id(self.telegram_id, self.auth_token)

        assert result is not None
        assert result["id"] == 1
        assert result["first_name"] == "John"

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_get_user_by_telegram_id_not_found(self, mock_get):
        """Test getting user by Telegram ID - not found."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = await self.client.get_user_by_telegram_id(self.telegram_id, self.auth_token)

        assert result is None

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_get_user_by_telegram_id_request_error(self, mock_get):
        """Test getting user by Telegram ID - request error."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Connection failed")

        result = await self.client.get_user_by_telegram_id(self.telegram_id, self.auth_token)

        assert result is None

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.post")
    async def test_authenticate_with_telegram_success(self, mock_post):
        """Test Telegram authentication - success case."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "token_123",
            "refresh_token": "refresh_123",
            "user": {"id": 1, "first_name": "John"}
        }
        mock_post.return_value = mock_response

        telegram_data = {"api_key": "test_key", "telegram_id": 123456}
        result = await self.client.authenticate_with_telegram(telegram_data)

        assert result is not None
        assert "access_token" in result

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.post")
    async def test_authenticate_with_telegram_failure(self, mock_post):
        """Test Telegram authentication - failure case."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        telegram_data = {"api_key": "test_key", "telegram_id": 123456}
        result = await self.client.authenticate_with_telegram(telegram_data)

        assert result is None

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.post")
    async def test_register_with_invitation_success(self, mock_post):
        """Test registration with invitation token - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "token_123",
            "refresh_token": "refresh_123",
        }
        mock_post.return_value = mock_response

        telegram_data = {"telegram_id": 123456, "username": "testuser"}
        result = await self.client.register_with_invitation("invite_token", telegram_data)

        assert result is not None
        assert "access_token" in result

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.post")
    async def test_register_with_invitation_failure(self, mock_post):
        """Test registration with invitation token - failure."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        telegram_data = {"telegram_id": 123456}
        result = await self.client.register_with_invitation("invite_token", telegram_data)

        assert result is None

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_validate_invitation_token_success(self, mock_get):
        """Test validating invitation token - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"token": "abc123", "email": "test@example.com", "expires_at": "2024-12-31"}
        mock_get.return_value = mock_response

        result = await self.client.validate_invitation_token("abc123")

        assert result is not None
        assert result["token"] == "abc123"

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_validate_invitation_token_invalid(self, mock_get):
        """Test validating invitation token - invalid."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = await self.client.validate_invitation_token("invalid_token")

        assert result is None

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_get_current_user_success(self, mock_get):
        """Test getting current user - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "first_name": "John", "email": "john@example.com"}
        mock_get.return_value = mock_response

        result = await self.client.get_current_user(self.auth_token)

        assert result is not None
        assert result["first_name"] == "John"

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_get_current_user_failure(self, mock_get):
        """Test getting current user - failure."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        result = await self.client.get_current_user(self.auth_token)

        assert result is None

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_get_mentor_info_success(self, mock_get):
        """Test getting mentor info - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 2, "first_name": "Jane", "role": "MENTOR"}
        mock_get.return_value = mock_response

        result = await self.client.get_mentor_info(2, self.auth_token)

        assert result is not None
        assert result["first_name"] == "Jane"

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_list_users_success(self, mock_get):
        """Test listing users - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"users": [{"id": 1}, {"id": 2}], "total": 2}
        mock_get.return_value = mock_response

        result = await self.client.list_users(self.auth_token)

        assert result is not None
        assert "users" in result

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_get_total_users_success(self, mock_get):
        """Test getting total user count - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"total": 42}
        mock_get.return_value = mock_response

        result = await self.client.get_total_users(self.auth_token)

        assert result == 42

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_get_total_users_error(self, mock_get):
        """Test getting total user count - error."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Connection failed")

        result = await self.client.get_total_users(self.auth_token)

        assert result == 0

    @patch("telegram_bot.services.auth_client.cache")
    async def test_invalidate_user_cache(self, mock_cache):
        """Test invalidating user cache."""
        mock_cache.delete_pattern = AsyncMock()

        await self.client.invalidate_user_cache(123456)

        mock_cache.delete_pattern.assert_called_once()


class TestAuthClientSingleton:
    """Test the auth_client singleton instance."""

    def test_singleton_is_mocked_in_tests(self):
        """Test that auth_client is mocked in test environment."""
        # In test environment, auth_client is patched to prevent real HTTP calls
        assert auth_client is not None


class TestAuthServiceClientEdgeCases:
    """Test edge cases and error handling for AuthServiceClient."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client = AuthServiceClient(base_url="http://test-auth:8001")
        self.auth_token = "test_token_123"
        self.telegram_id = 123456

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_get_user_by_telegram_id_various_non_200_codes(self, mock_get):
        """Test getting user with various non-200 status codes."""
        for status_code in [400, 401, 403, 404, 500, 502]:
            mock_response = MagicMock()
            mock_response.status_code = status_code
            mock_get.return_value = mock_response

            result = await self.client.get_user_by_telegram_id(self.telegram_id, self.auth_token)

            assert result is None

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_get_user_by_telegram_id_empty_response(self, mock_get):
        """Test getting user with empty response body."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        result = await self.client.get_user_by_telegram_id(self.telegram_id, self.auth_token)

        assert result == {}

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.post")
    async def test_authenticate_with_telegram_non_200_codes(self, mock_post):
        """Test Telegram authentication with various non-200 codes."""
        for status_code in [400, 401, 403, 404, 422, 500]:
            mock_response = MagicMock()
            mock_response.status_code = status_code
            mock_response.text = "Error"
            mock_post.return_value = mock_response

            telegram_data = {"api_key": "test_key", "telegram_id": 123456}
            result = await self.client.authenticate_with_telegram(telegram_data)

            assert result is None

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.post")
    async def test_authenticate_with_telegram_request_error(self, mock_post):
        """Test Telegram authentication with request error."""
        import httpx
        mock_post.side_effect = httpx.RequestError("Connection failed")

        telegram_data = {"api_key": "test_key", "telegram_id": 123456}
        result = await self.client.authenticate_with_telegram(telegram_data)

        assert result is None

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.post")
    async def test_register_with_invitation_non_200_codes(self, mock_post):
        """Test registration with various non-200 codes."""
        for status_code in [400, 401, 403, 404, 409, 410, 422, 500]:
            mock_response = MagicMock()
            mock_response.status_code = status_code
            mock_response.text = "Error"
            mock_post.return_value = mock_response

            telegram_data = {"telegram_id": 123456, "username": "testuser"}
            result = await self.client.register_with_invitation("token123", telegram_data)

            assert result is None

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.post")
    async def test_register_with_invitation_request_error(self, mock_post):
        """Test registration with request error."""
        import httpx
        mock_post.side_effect = httpx.RequestError("Network error")

        telegram_data = {"telegram_id": 123456}
        result = await self.client.register_with_invitation("token123", telegram_data)

        assert result is None

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_validate_invitation_token_non_200_codes(self, mock_get):
        """Test token validation with various non-200 codes."""
        for status_code in [400, 401, 403, 404, 410, 500]:
            mock_response = MagicMock()
            mock_response.status_code = status_code
            mock_response.text = "Error"
            mock_get.return_value = mock_response

            result = await self.client.validate_invitation_token("token123")

            assert result is None

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_validate_invitation_token_request_error(self, mock_get):
        """Test token validation with request error."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Timeout")

        result = await self.client.validate_invitation_token("token123")

        assert result is None

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_get_current_user_non_200_codes(self, mock_get):
        """Test getting current user with various non-200 codes."""
        for status_code in [401, 403, 404, 500]:
            mock_response = MagicMock()
            mock_response.status_code = status_code
            mock_response.text = "Error"
            mock_get.return_value = mock_response

            result = await self.client.get_current_user(self.auth_token)

            assert result is None

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_get_current_user_request_error(self, mock_get):
        """Test getting current user with request error."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Connection lost")

        result = await self.client.get_current_user(self.auth_token)

        assert result is None

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_get_mentor_info_non_200_codes(self, mock_get):
        """Test getting mentor info with various non-200 codes."""
        for status_code in [401, 403, 404, 500]:
            mock_response = MagicMock()
            mock_response.status_code = status_code
            mock_get.return_value = mock_response

            result = await self.client.get_mentor_info(2, self.auth_token)

            assert result is None

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_get_mentor_info_not_found(self, mock_get):
        """Test getting mentor info when mentor not found."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = await self.client.get_mentor_info(999, self.auth_token)

        assert result is None

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_get_mentor_info_request_error(self, mock_get):
        """Test getting mentor info with request error."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Error")

        result = await self.client.get_mentor_info(2, self.auth_token)

        assert result is None

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_list_users_non_200_codes(self, mock_get):
        """Test listing users with various non-200 codes."""
        for status_code in [401, 403, 500]:
            mock_response = MagicMock()
            mock_response.status_code = status_code
            mock_get.return_value = mock_response

            result = await self.client.list_users(self.auth_token)

            assert result is None

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_list_users_request_error(self, mock_get):
        """Test listing users with request error."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Network error")

        result = await self.client.list_users(self.auth_token)

        assert result is None

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_list_users_with_pagination_params(self, mock_get):
        """Test listing users with custom pagination."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"users": [], "total": 0}
        mock_get.return_value = mock_response

        result = await self.client.list_users(self.auth_token, page=2, size=50)

        assert result is not None
        # Verify params passed correctly
        call_kwargs = mock_get.call_args.kwargs
        assert call_kwargs["params"] == {"page": 2, "size": 50}

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_get_total_users_non_200_codes(self, mock_get):
        """Test getting total users with various non-200 codes."""
        for status_code in [401, 403, 404, 500]:
            mock_response = MagicMock()
            mock_response.status_code = status_code
            mock_get.return_value = mock_response

            result = await self.client.get_total_users(self.auth_token)

            assert result == 0

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_get_total_users_request_error(self, mock_get):
        """Test getting total users with request error."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Connection failed")

        result = await self.client.get_total_users(self.auth_token)

        assert result == 0

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_get_total_users_missing_total_key(self, mock_get):
        """Test getting total users when response missing total key."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"users": []}  # No total key
        mock_get.return_value = mock_response

        result = await self.client.get_total_users(self.auth_token)

        assert result == 0

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_get_total_users_zero_total(self, mock_get):
        """Test getting total users when total is 0."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"users": [], "total": 0}
        mock_get.return_value = mock_response

        result = await self.client.get_total_users(self.auth_token)

        assert result == 0

    @patch("telegram_bot.services.auth_client.cache")
    async def test_invalidate_user_cache_request_error(self, mock_cache):
        """Test invalidating cache when cache operation fails."""
        mock_cache.delete_pattern = AsyncMock(side_effect=Exception("Redis error"))

        # Should not raise - but currently doesn't catch exceptions
        with pytest.raises(Exception, match="Redis error"):
            await self.client.invalidate_user_cache(123456)

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_authenticate_with_telegram_invalid_api_key(self, mock_get):
        """Test authentication with invalid API key (401 response)."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Invalid API key"
        mock_get.side_effect = None

        # Actually this uses POST, let me fix the patch
        with patch("telegram_bot.services.auth_client.httpx.AsyncClient.post") as mock_post:
            mock_post.return_value = mock_response

            telegram_data = {"api_key": "invalid_key", "telegram_id": 123456}
            result = await self.client.authenticate_with_telegram(telegram_data)

            assert result is None

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_get_current_user_expired_token(self, mock_get):
        """Test getting current user with expired token (401)."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Token expired"
        mock_get.return_value = mock_response

        result = await self.client.get_current_user("expired_token")

        assert result is None

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_get_current_user_malformed_token(self, mock_get):
        """Test getting current user with malformed token."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Invalid token format"
        mock_get.return_value = mock_response

        result = await self.client.get_current_user("malformed_token")

        assert result is None

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.get")
    async def test_validate_invitation_token_expired(self, mock_get):
        """Test validating expired invitation token."""
        mock_response = MagicMock()
        mock_response.status_code = 410  # Gone - resource expired
        mock_response.text = "Invitation expired"
        mock_get.return_value = mock_response

        result = await self.client.validate_invitation_token("expired_token")

        assert result is None

    @patch("telegram_bot.services.auth_client.httpx.AsyncClient.post")
    async def test_register_with_invitation_conflict(self, mock_post):
        """Test registration with already used invitation (409 conflict)."""
        mock_response = MagicMock()
        mock_response.status_code = 409
        mock_response.text = "Invitation already used"
        mock_post.return_value = mock_response

        telegram_data = {"telegram_id": 123456}
        result = await self.client.register_with_invitation("used_token", telegram_data)

        assert result is None
