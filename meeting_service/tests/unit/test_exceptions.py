"""Unit tests for custom exceptions."""

from fastapi import status

from meeting_service.core.exceptions import (
    AuthException,
    ConflictException,
    NotFoundException,
    PermissionDenied,
    ValidationException,
)


class TestAuthException:
    """Tests for AuthException."""

    def test_default_auth_exception(self):
        """Test AuthException with default message."""
        exc = AuthException("Authentication required")

        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.detail == "Authentication required"
        assert exc.headers == {"WWW-Authenticate": "Bearer"}

    def test_custom_auth_exception(self):
        """Test AuthException with custom message."""
        exc = AuthException("Invalid token")

        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.detail == "Invalid token"
        assert exc.headers == {"WWW-Authenticate": "Bearer"}


class TestPermissionDenied:
    """Tests for PermissionDenied exception."""

    def test_default_permission_denied(self):
        """Test PermissionDenied with default message."""
        exc = PermissionDenied()

        assert exc.status_code == status.HTTP_403_FORBIDDEN
        assert exc.detail == "Permission denied"

    def test_custom_permission_denied(self):
        """Test PermissionDenied with custom message."""
        exc = PermissionDenied("Admin access required")

        assert exc.status_code == status.HTTP_403_FORBIDDEN
        assert exc.detail == "Admin access required"


class TestNotFoundException:
    """Tests for NotFoundException."""

    def test_default_not_found(self):
        """Test NotFoundException with default resource."""
        exc = NotFoundException()

        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert exc.detail == "Resource not found"

    def test_meeting_not_found(self):
        """Test NotFoundException for meeting resource."""
        exc = NotFoundException("Meeting")

        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert exc.detail == "Meeting not found"

    def test_user_not_found(self):
        """Test NotFoundException for user resource."""
        exc = NotFoundException("User")

        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert exc.detail == "User not found"


class TestValidationException:
    """Tests for ValidationException."""

    def test_validation_exception(self):
        """Test ValidationException."""
        exc = ValidationException("Invalid date format")

        assert exc.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert exc.detail == "Invalid date format"

    def test_validation_exception_with_details(self):
        """Test ValidationException with detailed message."""
        exc = ValidationException("scheduled_at must be in the future")

        assert exc.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert exc.detail == "scheduled_at must be in the future"


class TestConflictException:
    """Tests for ConflictException."""

    def test_conflict_exception(self):
        """Test ConflictException."""
        exc = ConflictException("Meeting already exists")

        assert exc.status_code == status.HTTP_409_CONFLICT
        assert exc.detail == "Meeting already exists"

    def test_conflict_exception_duplicate(self):
        """Test ConflictException for duplicate resource."""
        exc = ConflictException("User already assigned to this meeting")

        assert exc.status_code == status.HTTP_409_CONFLICT
        assert exc.detail == "User already assigned to this meeting"
