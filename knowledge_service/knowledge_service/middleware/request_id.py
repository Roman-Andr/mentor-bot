"""Request ID middleware for tracing requests across services."""

import uuid
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from knowledge_service.utils.logging import logger, request_id_var


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to inject or forward X-Request-ID header for request tracing."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        """Process request and inject request ID for tracing."""
        rid = request.headers.get("X-Request-ID")
        if rid is None:
            rid = uuid.uuid4().hex

        token = request_id_var.set(rid)

        response: Response | None = None
        try:
            with logger.contextualize(request_id=rid, method=request.method, path=request.url.path):
                result = await call_next(request)
                response = result
        finally:
            request_id_var.reset(token)

        if response is not None:
            response.headers["X-Request-ID"] = rid
        return response
