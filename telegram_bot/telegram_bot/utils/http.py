"""HTTP client utilities for making authenticated requests."""

from collections.abc import Callable
from typing import Any

import httpx

from telegram_bot.utils.logging import request_id_var


def inject_request_id(request: httpx.Request) -> None:
    """Inject request ID header into outgoing HTTP request."""
    rid = request_id_var.get()
    if rid is not None:
        request.headers["X-Request-ID"] = rid


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
