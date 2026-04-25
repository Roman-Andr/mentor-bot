"""Unit tests for utils/logging.py."""

import logging
from unittest.mock import MagicMock

import httpx

from feedback_service.utils.logging import (
    InterceptHandler,
    configure_logging,
    inject_request_id,
    request_id_var,
)


class TestInterceptHandlerEmit:
    """Tests for InterceptHandler.emit()."""

    def test_emit_basic_record(self) -> None:
        """Emits a basic record without raising."""
        handler = InterceptHandler()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="hello %s",
            args=("world",),
            exc_info=None,
        )
        handler.emit(record)

    def test_emit_with_exc_info_and_exc_text(self) -> None:
        """Emits a record that includes exc_text appended to the message."""
        handler = InterceptHandler()
        try:
            raise ValueError("boom")
        except ValueError:
            import sys

            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname=__file__,
            lineno=1,
            msg="error",
            args=None,
            exc_info=exc_info,
        )
        record.exc_text = "Traceback: boom"

        handler.emit(record)

    def test_emit_unknown_level_falls_back_to_info(self) -> None:
        """Unknown logging levels are mapped to INFO."""
        handler = InterceptHandler()
        record = logging.LogRecord(
            name="test",
            level=999,
            pathname=__file__,
            lineno=1,
            msg="weird level",
            args=None,
            exc_info=None,
        )
        handler.emit(record)

    def test_emit_calls_handle_error_on_exception(self) -> None:
        """When emit raises, handleError is called."""
        handler = InterceptHandler()
        handler.handleError = MagicMock()  # type: ignore[method-assign]

        record = MagicMock(spec=logging.LogRecord)
        record.levelno = logging.INFO
        record.exc_info = None
        record.exc_text = None
        record.getMessage.side_effect = RuntimeError("boom")

        handler.emit(record)

        handler.handleError.assert_called_once_with(record)


class TestConfigureLogging:
    """Tests for configure_logging()."""

    def test_configures_intercept_handler(self) -> None:
        """Replaces existing root handlers with InterceptHandler."""
        configure_logging("feedback_service", "INFO")
        assert any(isinstance(h, InterceptHandler) for h in logging.root.handlers)


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
