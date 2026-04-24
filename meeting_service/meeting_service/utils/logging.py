"""Logging configuration and utilities."""

import logging
import sys
from contextvars import ContextVar

import httpx
import loguru
from loguru import logger

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


class InterceptHandler(logging.Handler):
    """Handler to intercept standard logging and forward to loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to loguru."""
        try:
            level_map = {
                logging.DEBUG: "DEBUG",
                logging.INFO: "INFO",
                logging.WARNING: "WARNING",
                logging.ERROR: "ERROR",
                logging.CRITICAL: "CRITICAL",
            }
            level_name = level_map.get(record.levelno, "INFO")

            msg = record.getMessage()
            if record.exc_info and record.exc_text:
                msg += "\n" + record.exc_text

            loguru.logger.log(level_name, msg)
        except Exception:
            self.handleError(record)


def configure_logging(service_name: str, log_level: str) -> None:
    """Configure logging for the service."""
    logger.remove()

    logger.add(
        sys.stdout,
        serialize=True,
        level=log_level,
        format="{message}",
    )

    logger.configure(extra={"service": service_name})

    intercept_handler = InterceptHandler()
    logging.root.addHandler(intercept_handler)
    logging.root.setLevel(logging.NOTSET)
    for handler in logging.root.handlers[:]:
        if handler != intercept_handler:
            logging.root.removeHandler(handler)

    quiet_loggers = [
        ("uvicorn.access", logging.WARNING),
        ("sqlalchemy.engine", logging.WARNING),
        ("sqlalchemy.pool", logging.WARNING),
        ("httpx", logging.WARNING),
        ("httpcore", logging.WARNING),
        ("asyncio", logging.WARNING),
        ("aiogram.event", logging.INFO),
        ("apscheduler", logging.WARNING),
    ]
    for name, level in quiet_loggers:
        logging.getLogger(name).setLevel(level)


def inject_request_id(request: httpx.Request) -> None:
    """Inject request ID header into outgoing HTTP request."""
    rid = request_id_var.get()
    if rid is not None:
        request.headers["X-Request-ID"] = rid
