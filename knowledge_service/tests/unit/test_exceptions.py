"""Tests for custom exceptions - covering line 56 (ConflictException)."""

from fastapi import status

from knowledge_service.core.exceptions import (
    AuthException,
    ConflictException,
    NotFoundException,
    PermissionDenied,
    ValidationException,
)


class TestAuthException:
    """Test AuthException."""

    def test_auth_exception(self):
        """Test AuthException initialization."""
        exc = AuthException("Invalid credentials")

        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.detail == "Invalid credentials"
        assert exc.headers == {"WWW-Authenticate": "Bearer"}


class TestPermissionDenied:
    """Test PermissionDenied exception."""

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
    """Test NotFoundException."""

    def test_not_found_default(self):
        """Test NotFoundException with default resource."""
        exc = NotFoundException()

        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert exc.detail == "Resource not found"

    def test_not_found_custom(self):
        """Test NotFoundException with custom resource."""
        exc = NotFoundException("Article")

        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert exc.detail == "Article not found"


class TestValidationException:
    """Test ValidationException."""

    def test_validation_exception(self):
        """Test ValidationException initialization."""
        exc = ValidationException("Invalid file type")

        assert exc.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert exc.detail == "Invalid file type"


class TestConflictException:
    """
    Test ConflictException - covers line 56.

    This tests the ConflictException which was previously uncovered.
    """

    def test_conflict_exception(self):
        """Test ConflictException initialization - covers line 56."""
        exc = ConflictException("Department already exists")

        assert exc.status_code == status.HTTP_409_CONFLICT
        assert exc.detail == "Department already exists"

    def test_conflict_exception_duplicate_resource(self):
        """Test ConflictException for duplicate resource."""
        exc = ConflictException("Resource with this name already exists")

        assert exc.status_code == status.HTTP_409_CONFLICT
        assert exc.detail == "Resource with this name already exists"
