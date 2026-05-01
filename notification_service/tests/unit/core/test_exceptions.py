"""Unit tests for notification_service/core/exceptions.py."""

import pytest
from fastapi import HTTPException
from notification_service.core.exceptions import (
    AuthException,
    ConflictException,
    NotFoundException,
    NotificationException,
    PermissionDenied,
    ValidationException,
)


class TestNotificationException:
    """Tests for NotificationException."""

    def test_inherits_from_http_exception(self) -> None:
        """NotificationException inherits from HTTPException."""
        assert issubclass(NotificationException, HTTPException)

    def test_can_be_raised_with_message(self) -> None:
        """Exception can be raised with a custom message."""
        test_message = "Test error message"
        with pytest.raises(NotificationException, match=test_message):
            raise NotificationException(test_message)

    def test_has_500_status_code(self) -> None:
        """NotificationException has 500 status code."""
        exc = NotificationException("Server error")
        assert exc.status_code == 500
        assert exc.detail == "Server error"


class TestAuthException:
    """Tests for AuthException."""

    def test_inherits_from_http_exception(self) -> None:
        """AuthException inherits from HTTPException."""
        assert issubclass(AuthException, HTTPException)

    def test_custom_message(self) -> None:
        """Can provide custom authentication error message."""
        exc = AuthException("Invalid token provided")
        assert exc.detail == "Invalid token provided"

    def test_can_be_caught_as_http_exception(self) -> None:
        """AuthException can be caught as HTTPException."""
        auth_failed_message = "Auth failed"
        with pytest.raises(HTTPException):
            raise AuthException(auth_failed_message)

    def test_has_401_status_code(self) -> None:
        """AuthException has 401 status code."""
        exc = AuthException("Auth failed")
        assert exc.status_code == 401

    def test_has_www_authenticate_header(self) -> None:
        """AuthException includes WWW-Authenticate header."""
        exc = AuthException("Auth failed")
        assert exc.headers == {"WWW-Authenticate": "Bearer"}


class TestPermissionDenied:
    """Tests for PermissionDenied exception."""

    def test_inherits_from_http_exception(self) -> None:
        """PermissionDenied inherits from HTTPException."""
        assert issubclass(PermissionDenied, HTTPException)

    def test_default_message(self) -> None:
        """Default message indicates permission error."""
        exc = PermissionDenied()
        assert "Permission denied" in exc.detail

    def test_custom_message(self) -> None:
        """Can provide custom permission error message."""
        exc = PermissionDenied("Admin access required")
        assert exc.detail == "Admin access required"

    def test_can_be_caught_as_http_exception(self) -> None:
        """PermissionDenied can be caught as HTTPException."""
        no_access_message = "No access"
        with pytest.raises(HTTPException):
            raise PermissionDenied(no_access_message)

    def test_has_403_status_code(self) -> None:
        """PermissionDenied has 403 status code."""
        exc = PermissionDenied("No access")
        assert exc.status_code == 403


class TestNotFoundException:
    """Tests for NotFoundException."""

    def test_inherits_from_http_exception(self) -> None:
        """NotFoundException inherits from HTTPException."""
        assert issubclass(NotFoundException, HTTPException)

    def test_default_resource_message(self) -> None:
        """Default message for generic resource."""
        exc = NotFoundException()
        assert "Resource not found" in exc.detail

    def test_custom_resource_message(self) -> None:
        """Custom resource name in message."""
        exc = NotFoundException("Notification")
        assert "Notification not found" in exc.detail

    def test_has_404_status_code(self) -> None:
        """NotFoundException has 404 status code."""
        exc = NotFoundException("Item")
        assert exc.status_code == 404


class TestValidationException:
    """Tests for ValidationException."""

    def test_inherits_from_http_exception(self) -> None:
        """ValidationException inherits from HTTPException."""
        assert issubclass(ValidationException, HTTPException)

    def test_custom_message(self) -> None:
        """Can provide custom validation error message."""
        exc = ValidationException("Invalid email format")
        assert exc.detail == "Invalid email format"

    def test_has_422_status_code(self) -> None:
        """ValidationException has 422 status code."""
        exc = ValidationException("Invalid data")
        assert exc.status_code == 422


class TestConflictException:
    """Tests for ConflictException."""

    def test_inherits_from_http_exception(self) -> None:
        """ConflictException inherits from HTTPException."""
        assert issubclass(ConflictException, HTTPException)

    def test_custom_message(self) -> None:
        """Can provide custom conflict error message."""
        exc = ConflictException("Resource already exists")
        assert exc.detail == "Resource already exists"

    def test_has_409_status_code(self) -> None:
        """ConflictException has 409 status code."""
        exc = ConflictException("Duplicate")
        assert exc.status_code == 409


class TestExceptionHierarchies:
    """Tests for exception hierarchy relationships."""

    def test_all_exceptions_caught_as_http_exception(self) -> None:
        """All custom exceptions can be caught as HTTPException."""
        exceptions = [
            AuthException("Auth failed"),
            PermissionDenied("No permission"),
            ValidationException("Invalid data"),
            NotFoundException("Item"),
            ConflictException("Conflict"),
            NotificationException("Error"),
        ]

        for exc in exceptions:
            with pytest.raises(HTTPException):
                raise exc

    def test_exception_attributes(self) -> None:
        """Exceptions preserve their attributes."""
        exc = AuthException("Test message")
        assert hasattr(exc, "detail")
        assert exc.detail == "Test message"


class TestHTTPExceptionProperties:
    """Tests for HTTPException-specific properties."""

    def test_all_exceptions_have_status_code(self) -> None:
        """All exceptions have appropriate status codes."""
        assert AuthException("test").status_code == 401
        assert PermissionDenied("test").status_code == 403
        assert NotFoundException("test").status_code == 404
        assert ConflictException("test").status_code == 409
        assert ValidationException("test").status_code == 422
        assert NotificationException("test").status_code == 500
