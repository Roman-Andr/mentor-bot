"""Unit tests for utils/http.py."""

import httpx
from telegram_bot.utils.http import inject_request_id, make_async_client
from telegram_bot.utils.logging import request_id_var


class TestMakeAsyncClient:
    """Tests for make_async_client()."""

    def test_returns_httpx_async_client(self) -> None:
        """Returns an httpx.AsyncClient instance."""
        client = make_async_client()
        assert isinstance(client, httpx.AsyncClient)

    def test_registers_inject_request_id_hook(self) -> None:
        """Registers inject_request_id as a request event hook."""
        client = make_async_client()
        hooks = client.event_hooks.get("request", [])
        assert inject_request_id in hooks

    def test_preserves_existing_request_hooks_list(self) -> None:
        """Preserves existing request hooks while injecting our hook first."""

        def existing_hook(request: httpx.Request) -> None:
            return None

        client = make_async_client(event_hooks={"request": [existing_hook]})
        hooks = client.event_hooks.get("request", [])
        assert hooks[0] is inject_request_id
        assert existing_hook in hooks

    def test_handles_non_list_request_hooks(self) -> None:
        """Replaces non-list request hooks with a list containing our hook."""

        def existing_hook(request: httpx.Request) -> None:
            return None

        client = make_async_client(event_hooks={"request": existing_hook})
        hooks = client.event_hooks.get("request", [])
        assert hooks == [inject_request_id]

    def test_passes_other_kwargs_through(self) -> None:
        """Other kwargs like base_url are forwarded to httpx.AsyncClient."""
        client = make_async_client(base_url="http://example.com")
        assert str(client.base_url).rstrip("/") == "http://example.com"


class TestInjectRequestId:
    """Tests for inject_request_id()."""

    def test_no_header_when_request_id_is_none(self) -> None:
        """No header is added when context var is unset."""
        request = httpx.Request("GET", "http://example.com")
        token = request_id_var.set(None)
        try:
            inject_request_id(request)
        finally:
            request_id_var.reset(token)
        assert "X-Request-ID" not in request.headers

    def test_adds_header_when_request_id_present(self) -> None:
        """Adds X-Request-ID header when context var is set."""
        request = httpx.Request("GET", "http://example.com")
        token = request_id_var.set("abc-123")
        try:
            inject_request_id(request)
        finally:
            request_id_var.reset(token)
        assert request.headers.get("X-Request-ID") == "abc-123"
