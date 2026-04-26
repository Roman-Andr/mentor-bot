"""Unit tests for RequestIDMiddleware."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from starlette.requests import Request
from starlette.responses import Response

from escalation_service.middleware.request_id import RequestIDMiddleware
from escalation_service.utils.logging import request_id_var


def _build_request() -> Request:
    """Build a minimal ASGI Starlette Request."""
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/test",
        "raw_path": b"/test",
        "query_string": b"",
        "headers": [],
        "scheme": "http",
        "server": ("testserver", 80),
        "root_path": "",
    }
    return Request(scope)


def _build_request_with_rid(rid: str) -> Request:
    """Build a request with X-Request-ID header set."""
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/test",
        "raw_path": b"/test",
        "query_string": b"",
        "headers": [(b"x-request-id", rid.encode())],
        "scheme": "http",
        "server": ("testserver", 80),
        "root_path": "",
    }
    return Request(scope)


class TestRequestIDMiddleware:
    """Tests for RequestIDMiddleware.dispatch."""

    @pytest.mark.asyncio
    async def test_generates_request_id_when_not_provided(self) -> None:
        """Generates a new request ID when X-Request-ID header is absent."""
        middleware = RequestIDMiddleware(app=MagicMock())
        request = _build_request()

        response = Response("ok")
        call_next = AsyncMock(return_value=response)

        result = await middleware.dispatch(request, call_next)

        assert result is response
        rid = result.headers.get("X-Request-ID")
        assert rid is not None
        assert len(rid) == 32  # uuid4().hex
        # context var was reset
        assert request_id_var.get() is None

    @pytest.mark.asyncio
    async def test_uses_existing_request_id_header(self) -> None:
        """Uses incoming X-Request-ID header when present."""
        middleware = RequestIDMiddleware(app=MagicMock())
        request = _build_request_with_rid("incoming-rid-42")

        response = Response("ok")
        call_next = AsyncMock(return_value=response)

        result = await middleware.dispatch(request, call_next)

        assert result.headers.get("X-Request-ID") == "incoming-rid-42"

    @pytest.mark.asyncio
    async def test_request_id_var_set_during_call_next(self) -> None:
        """request_id_var is set during the downstream call."""
        middleware = RequestIDMiddleware(app=MagicMock())
        request = _build_request_with_rid("ctx-rid")

        captured: dict[str, str | None] = {}

        async def capture(_req: Request) -> Response:
            captured["rid"] = request_id_var.get()
            return Response("ok")

        await middleware.dispatch(request, capture)

        assert captured["rid"] == "ctx-rid"
        assert request_id_var.get() is None

    @pytest.mark.asyncio
    async def test_resets_context_var_when_call_next_raises(self) -> None:
        """Even if call_next raises, request_id_var is reset."""
        middleware = RequestIDMiddleware(app=MagicMock())
        request = _build_request_with_rid("err-rid")

        async def boom(_req: Request) -> Response:
            raise RuntimeError("boom")

        with pytest.raises(RuntimeError):
            await middleware.dispatch(request, boom)

        assert request_id_var.get() is None

    @pytest.mark.asyncio
    async def test_logs_error_for_5xx_status(self) -> None:
        """Logs error for 5xx status codes."""
        middleware = RequestIDMiddleware(app=MagicMock())
        request = _build_request()

        response = Response("error", status_code=500)
        call_next = AsyncMock(return_value=response)

        result = await middleware.dispatch(request, call_next)

        assert result is response
        assert result.headers.get("X-Request-ID") is not None

    @pytest.mark.asyncio
    async def test_logs_warning_for_4xx_status(self) -> None:
        """Logs warning for 4xx status codes."""
        middleware = RequestIDMiddleware(app=MagicMock())
        request = _build_request()

        response = Response("not found", status_code=404)
        call_next = AsyncMock(return_value=response)

        result = await middleware.dispatch(request, call_next)

        assert result is response
        assert result.headers.get("X-Request-ID") is not None
