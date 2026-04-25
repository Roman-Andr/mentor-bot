"""Request ID middleware for tracing requests across services."""

import uuid
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from escalation_service.utils.logging import logger, request_id_var


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
                logger.debug("HTTP request received: {} {}", request.method, request.url.path)
                try:
                    result = await call_next(request)
                except Exception:
                    logger.exception(
                        "Unhandled exception during request: {} {}",
                        request.method,
                        request.url.path,
                    )
                    raise
                response = result
                if response is not None and response.status_code >= 500:
                    logger.error(
                        "HTTP {} {} -> {}",
                        request.method,
                        request.url.path,
                        response.status_code,
                    )
                elif response is not None and response.status_code >= 400:
                    logger.warning(
                        "HTTP {} {} -> {}",
                        request.method,
                        request.url.path,
                        response.status_code,
                    )
                else:
                    logger.debug(
                        "HTTP {} {} -> {}",
                        request.method,
                        request.url.path,
                        response.status_code if response is not None else "no_response",
                    )
        finally:
            request_id_var.reset(token)

        if response is not None:
            response.headers["X-Request-ID"] = rid
        return response
