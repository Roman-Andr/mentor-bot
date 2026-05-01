"""Unit tests for utils/http.py."""

import os

import httpx
from notification_service.utils.http import make_async_client
from notification_service.utils.logging import inject_request_id

# Clear proxy environment variables to avoid httpx proxy errors
# httpx doesn't support 'socks://' scheme, only 'socks5://' and 'socks5h://'
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("all_proxy", None)
os.environ.pop("ALL_PROXY", None)


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
