"""Unit tests for auth_service/core/exceptions.py."""

from auth_service.core import AuthException, ConflictException, NotFoundException, PermissionDenied, ValidationException


class TestAuthException:
    """Tests for AuthException."""

    def test_auth_exception_initialization(self):
        """Test AuthException initializes with correct status code and headers."""
        exc = AuthException("Invalid credentials")
        assert exc.status_code == 401
        assert exc.detail == "Invalid credentials"
        assert exc.headers == {"WWW-Authenticate": "Bearer"}


class TestPermissionDenied:
    """Tests for PermissionDenied."""

    def test_permission_denied_default_message(self):
        """Test PermissionDenied uses default message when none provided."""
        exc = PermissionDenied()
        assert exc.status_code == 403
        assert exc.detail == "Permission denied"

    def test_permission_denied_custom_message(self):
        """Test PermissionDenied uses custom message when provided."""
        exc = PermissionDenied("You cannot access this resource")
        assert exc.status_code == 403
        assert exc.detail == "You cannot access this resource"


class TestNotFoundException:
    """Tests for NotFoundException."""

    def test_not_found_default_resource(self):
        """Test NotFoundException uses default resource when none provided."""
        exc = NotFoundException()
        assert exc.status_code == 404
        assert exc.detail == "Resource not found"

    def test_not_found_custom_resource(self):
        """Test NotFoundException uses custom resource when provided."""
        exc = NotFoundException("User")
        assert exc.status_code == 404
        assert exc.detail == "User not found"


class TestValidationException:
    """Tests for ValidationException."""

    def test_validation_exception_initialization(self):
        """Test ValidationException initializes with correct status code and detail."""
        exc = ValidationException("Invalid email format")
        assert exc.status_code == 422
        assert exc.detail == "Invalid email format"


class TestConflictException:
    """Tests for ConflictException."""

    def test_conflict_exception_initialization(self):
        """Test ConflictException initializes with correct status code and detail."""
        exc = ConflictException("Email already registered")
        assert exc.status_code == 409
        assert exc.detail == "Email already registered"
