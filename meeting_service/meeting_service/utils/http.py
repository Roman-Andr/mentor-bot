"""HTTP client utilities for making authenticated requests."""

from collections.abc import Callable
from typing import Any

import httpx

from meeting_service.utils.logging import inject_request_id


def make_async_client(**kwargs: Any) -> httpx.AsyncClient:
    """Create an httpx.AsyncClient with request ID injection."""
    existing_hooks = kwargs.pop("event_hooks", {})
    request_hooks: list[Callable[[httpx.Request], None]] = existing_hooks.get("request", [])
    if isinstance(request_hooks, list):
        request_hooks = list(request_hooks)
        request_hooks.insert(0, inject_request_id)
    else:
        request_hooks = [inject_request_id]

    kwargs["event_hooks"] = {"request": request_hooks}
    return httpx.AsyncClient(**kwargs)
