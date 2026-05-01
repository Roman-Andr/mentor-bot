"""Unit tests for auth_service/middleware/request_id.py."""

from unittest.mock import MagicMock, patch

import pytest

from auth_service.middleware.request_id import RequestIDMiddleware


class TestRequestIDMiddleware:
    """Tests for RequestIDMiddleware."""

    @pytest.mark.asyncio
    async def test_dispatch_injects_request_id_from_header(self):
        """Test middleware uses existing X-Request-ID from header."""
        middleware = RequestIDMiddleware(app=MagicMock())
        mock_request = MagicMock()
        mock_request.headers.get = MagicMock(return_value="existing-request-id")
        mock_request.method = "GET"
        mock_request.url.path = "/test"

        async def call_next(request):
            response = MagicMock()
            response.status_code = 200
            response.headers = {}
            return response

        response = await middleware.dispatch(mock_request, call_next)

        assert response.headers["X-Request-ID"] == "existing-request-id"

    @pytest.mark.asyncio
    async def test_dispatch_generates_new_request_id(self):
        """Test middleware generates new X-Request-ID when not present."""
        middleware = RequestIDMiddleware(app=MagicMock())
        mock_request = MagicMock()
        mock_request.headers.get = MagicMock(return_value=None)
        mock_request.method = "GET"
        mock_request.url.path = "/test"

        async def call_next(request):
            response = MagicMock()
            response.status_code = 200
            response.headers = {}
            return response

        response = await middleware.dispatch(mock_request, call_next)

        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) == 32  # UUID hex length

    @pytest.mark.asyncio
    async def test_dispatch_logs_5xx_error(self):
        """Test middleware logs error for 5xx responses."""
        middleware = RequestIDMiddleware(app=MagicMock())
        mock_request = MagicMock()
        mock_request.headers.get = MagicMock(return_value="test-id")
        mock_request.method = "GET"
        mock_request.url.path = "/test"

        async def call_next(request):
            response = MagicMock()
            response.status_code = 500
            response.headers = {}
            return response

        with patch("auth_service.middleware.request_id.logger") as mock_logger:
            await middleware.dispatch(mock_request, call_next)

            # Verify error was logged
            assert mock_logger.error.called

    @pytest.mark.asyncio
    async def test_dispatch_logs_4xx_warning(self):
        """Test middleware logs warning for 4xx responses."""
        middleware = RequestIDMiddleware(app=MagicMock())
        mock_request = MagicMock()
        mock_request.headers.get = MagicMock(return_value="test-id")
        mock_request.method = "GET"
        mock_request.url.path = "/test"

        async def call_next(request):
            response = MagicMock()
            response.status_code = 404
            response.headers = {}
            return response

        with patch("auth_service.middleware.request_id.logger") as mock_logger:
            await middleware.dispatch(mock_request, call_next)

            # Verify warning was logged
            assert mock_logger.warning.called

    @pytest.mark.asyncio
    async def test_dispatch_logs_debug_for_2xx(self):
        """Test middleware logs debug for successful responses."""
        middleware = RequestIDMiddleware(app=MagicMock())
        mock_request = MagicMock()
        mock_request.headers.get = MagicMock(return_value="test-id")
        mock_request.method = "GET"
        mock_request.url.path = "/test"

        async def call_next(request):
            response = MagicMock()
            response.status_code = 200
            response.headers = {}
            return response

        with patch("auth_service.middleware.request_id.logger") as mock_logger:
            await middleware.dispatch(mock_request, call_next)

            # Verify debug was logged
            assert mock_logger.debug.called

    @pytest.mark.asyncio
    async def test_dispatch_handles_exception(self):
        """Test middleware logs and re-raises exceptions."""
        middleware = RequestIDMiddleware(app=MagicMock())
        mock_request = MagicMock()
        mock_request.headers.get = MagicMock(return_value="test-id")
        mock_request.method = "GET"
        mock_request.url.path = "/test"

        async def call_next(request):
            raise ValueError("Test error")

        with patch("auth_service.middleware.request_id.logger") as mock_logger:
            with pytest.raises(ValueError, match="Test error"):
                await middleware.dispatch(mock_request, call_next)

            # Verify exception was logged
            assert mock_logger.exception.called

    @pytest.mark.asyncio
    async def test_dispatch_resets_context_on_exception(self):
        """Test middleware resets context even on exception."""
        middleware = RequestIDMiddleware(app=MagicMock())
        mock_request = MagicMock()
        mock_request.headers.get = MagicMock(return_value="test-id")
        mock_request.method = "GET"
        mock_request.url.path = "/test"

        async def call_next(request):
            raise ValueError("Test error")

        with patch("auth_service.middleware.request_id.request_id_var") as mock_var:
            mock_var.set.return_value = "token"
            mock_var.reset = MagicMock()

            with pytest.raises(ValueError):
                await middleware.dispatch(mock_request, call_next)

            # Verify context was reset
            mock_var.reset.assert_called_once_with("token")

    @pytest.mark.asyncio
    async def test_dispatch_handles_none_response(self):
        """Test middleware handles None response gracefully."""
        middleware = RequestIDMiddleware(app=MagicMock())
        mock_request = MagicMock()
        mock_request.headers.get = MagicMock(return_value="test-id")
        mock_request.method = "GET"
        mock_request.url.path = "/test"

        async def call_next(request):
            return None

        response = await middleware.dispatch(mock_request, call_next)

        assert response is None
