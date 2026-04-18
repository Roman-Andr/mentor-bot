"""Tests for core/exceptions.py."""

from fastapi import HTTPException, status

from checklists_service.core.exceptions import (
    AuthException,
    ConflictException,
    NotFoundException,
    PermissionDenied,
    ValidationException,
)


class TestAuthException:
    """Test AuthException class."""

    def test_auth_exception_default(self):
        """Test AuthException with default parameters."""
        exc = AuthException("Invalid credentials")

        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.detail == "Invalid credentials"
        assert exc.headers == {"WWW-Authenticate": "Bearer"}

    def test_auth_exception_is_http_exception(self):
        """Test AuthException is a subclass of HTTPException."""
        exc = AuthException("Test")
        assert isinstance(exc, HTTPException)

    def test_auth_exception_line_11(self):
        """Test AuthException line 11 - super().__init__ call."""
        # This test covers line 11 of exceptions.py
        detail = "Test authentication error"
        exc = AuthException(detail)

        assert exc.status_code == 401
        assert exc.detail == detail
        assert exc.headers == {"WWW-Authenticate": "Bearer"}


class TestPermissionDenied:
    """Test PermissionDenied class."""

    def test_permission_denied_default(self):
        """Test PermissionDenied with default message."""
        exc = PermissionDenied()

        assert exc.status_code == status.HTTP_403_FORBIDDEN
        assert exc.detail == "Permission denied"

    def test_permission_denied_custom(self):
        """Test PermissionDenied with custom message."""
        exc = PermissionDenied("Admin access required")

        assert exc.status_code == status.HTTP_403_FORBIDDEN
        assert exc.detail == "Admin access required"


class TestNotFoundException:
    """Test NotFoundException class."""

    def test_not_found_default(self):
        """Test NotFoundException with default resource."""
        exc = NotFoundException()

        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert exc.detail == "Resource not found"

    def test_not_found_custom(self):
        """Test NotFoundException with custom resource."""
        exc = NotFoundException("Checklist")

        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert exc.detail == "Checklist not found"

    def test_not_found_different_resources(self):
        """Test NotFoundException with different resource types."""
        test_cases = [
            ("User", "User not found"),
            ("Template", "Template not found"),
            ("Task", "Task not found"),
            ("Department", "Department not found"),
        ]

        for resource, expected_detail in test_cases:
            exc = NotFoundException(resource)
            assert exc.detail == expected_detail


class TestValidationException:
    """Test ValidationException class."""

    def test_validation_exception(self):
        """Test ValidationException."""
        exc = ValidationException("Invalid input data")

        assert exc.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert exc.detail == "Invalid input data"

    def test_validation_exception_complex_message(self):
        """Test ValidationException with complex message."""
        detail = "Field 'email' must be a valid email address"
        exc = ValidationException(detail)

        assert exc.detail == detail


class TestConflictException:
    """Test ConflictException class."""

    def test_conflict_exception(self):
        """Test ConflictException."""
        exc = ConflictException("Resource already exists")

        assert exc.status_code == status.HTTP_409_CONFLICT
        assert exc.detail == "Resource already exists"

    def test_conflict_exception_duplicate(self):
        """Test ConflictException for duplicate resource."""
        exc = ConflictException("User with this email already exists")

        assert exc.status_code == 409
        assert "already exists" in exc.detail
