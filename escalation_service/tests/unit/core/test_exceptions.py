"""Unit tests for escalation_service/core/exceptions.py."""

from fastapi import status

from escalation_service.core.exceptions import (
    AuthException,
    ConflictException,
    NotFoundException,
    PermissionDenied,
    ValidationException,
)


class TestValidationException:
    """Tests for ValidationException (line 45)."""

    def test_validation_exception_init(self):
        """Test ValidationException initialization with detail."""
        detail = "Invalid field value"
        exc = ValidationException(detail)

        assert exc.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert exc.detail == detail

    def test_validation_exception_with_different_messages(self):
        """Test ValidationException with various error messages."""
        test_cases = [
            "Field is required",
            "Invalid email format",
            "Value must be greater than 0",
            "Date must be in the future",
        ]

        for message in test_cases:
            exc = ValidationException(message)
            assert exc.status_code == 422
            assert exc.detail == message


class TestConflictException:
    """Tests for ConflictException (line 56)."""

    def test_conflict_exception_init(self):
        """Test ConflictException initialization with detail."""
        detail = "Resource already exists"
        exc = ConflictException(detail)

        assert exc.status_code == status.HTTP_409_CONFLICT
        assert exc.detail == detail

    def test_conflict_exception_with_different_messages(self):
        """Test ConflictException with various error messages."""
        test_cases = [
            "Duplicate entry found",
            "User already exists",
            "Escalation request already pending",
            "Record with this ID already exists",
        ]

        for message in test_cases:
            exc = ConflictException(message)
            assert exc.status_code == 409
            assert exc.detail == message


class TestAuthException:
    """Tests for AuthException."""

    def test_auth_exception_init(self):
        """Test AuthException initialization."""
        detail = "Invalid credentials"
        exc = AuthException(detail)

        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.detail == detail
        assert exc.headers == {"WWW-Authenticate": "Bearer"}

    def test_auth_exception_with_different_messages(self):
        """Test AuthException with various messages."""
        test_cases = [
            "Token expired",
            "Invalid signature",
            "Missing authentication",
        ]

        for message in test_cases:
            exc = AuthException(message)
            assert exc.status_code == 401
            assert exc.headers == {"WWW-Authenticate": "Bearer"}


class TestPermissionDenied:
    """Tests for PermissionDenied exception."""

    def test_permission_denied_init(self):
        """Test PermissionDenied initialization."""
        detail = "Admin access required"
        exc = PermissionDenied(detail)

        assert exc.status_code == status.HTTP_403_FORBIDDEN
        assert exc.detail == detail

    def test_permission_denied_default_message(self):
        """Test PermissionDenied with default message."""
        exc = PermissionDenied()

        assert exc.status_code == 403
        assert exc.detail == "Permission denied"


class TestNotFoundException:
    """Tests for NotFoundException."""

    def test_not_found_exception_init(self):
        """Test NotFoundException initialization."""
        resource = "Escalation request"
        exc = NotFoundException(resource)

        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert exc.detail == "Escalation request not found"

    def test_not_found_exception_default(self):
        """Test NotFoundException with default resource."""
        exc = NotFoundException()

        assert exc.status_code == 404
        assert exc.detail == "Resource not found"

    def test_not_found_exception_various_resources(self):
        """Test NotFoundException with different resource types."""
        test_cases = [
            ("User", "User not found"),
            ("Department", "Department not found"),
            ("Employee", "Employee not found"),
            ("Task", "Task not found"),
        ]

        for resource, expected_detail in test_cases:
            exc = NotFoundException(resource)
            assert exc.status_code == 404
            assert exc.detail == expected_detail
