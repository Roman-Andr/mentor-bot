"""Logging configuration and utilities."""

import logging
import sys
from contextvars import ContextVar
from pathlib import Path
from types import FrameType

import httpx
import loguru
from loguru import logger

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)

LOG_DIR = Path("/var/log/app")


class InterceptHandler(logging.Handler):
    """Forward stdlib logging records to loguru, preserving caller info."""

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to loguru."""
        try:
            level: str | int
            try:
                level = loguru.logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # Walk up the stack until we exit stdlib logging — works regardless
            # of how shallow the call stack is (uvicorn boot logs hit emit()
            # with fewer frames than a normal logger.info from app code).
            frame: FrameType | None = logging.currentframe()
            depth = 2
            while frame is not None and frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            loguru.logger.opt(depth=depth, exception=record.exc_info).log(
                level,
                record.getMessage(),
            )
        except Exception:
            self.handleError(record)


def configure_logging(service_name: str, log_level: str) -> None:
    """Configure two-sink logging: pretty stdout + JSON file at /var/log/app/<svc>.log."""  # noqa: E501
    logger.remove()

    logger.add(
        sys.stdout,
        level=log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        colorize=False,
    )

    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        logger.add(
            LOG_DIR / f"{service_name}.log",
            level=log_level,
            serialize=True,
            format="{message}",
            rotation="50 MB",
            retention=5,
        )
    except OSError:
        pass

    logger.configure(extra={"service": service_name})

    intercept_handler = InterceptHandler()
    logging.root.handlers = [intercept_handler]
    logging.root.setLevel(logging.NOTSET)

    # Frameworks (uvicorn, fastapi) attach their own StreamHandlers via
    # logging.config.dictConfig and set propagate=False, which bypasses the
    # root InterceptHandler. Replace their handlers with ours directly so
    # every record flows through loguru regardless of propagation.
    intercepted_loggers = (
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "uvicorn.asgi",
        "fastapi",
        "alembic",
        "alembic.runtime.migration",
        "watchfiles",
        "watchfiles.main",
    )
    for name in intercepted_loggers:
        lg = logging.getLogger(name)
        lg.handlers = [intercept_handler]
        lg.propagate = False

    quiet_loggers = [
        ("uvicorn.access", logging.WARNING),
        ("sqlalchemy.engine", logging.WARNING),
        ("sqlalchemy.pool", logging.WARNING),
        ("httpx", logging.WARNING),
        ("httpcore", logging.WARNING),
        ("asyncio", logging.WARNING),
        ("aiogram.event", logging.INFO),
        ("apscheduler", logging.WARNING),
        ("watchfiles", logging.WARNING),
    ]
    for name, level in quiet_loggers:
        logging.getLogger(name).setLevel(level)


def inject_request_id(request: httpx.Request) -> None:
    """Inject request ID header into outgoing HTTP request."""
    rid = request_id_var.get()
    if rid is not None:
        request.headers["X-Request-ID"] = rid
