"""Custom exceptions for the Notification Service."""

from fastapi import HTTPException, status


class AuthException(HTTPException):
    """Base authentication exception."""

    def __init__(self, detail: str) -> None:
        """Initialize authentication exception with custom detail message."""
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class PermissionDenied(HTTPException):
    """Permission denied exception."""

    def __init__(self, detail: str = "Permission denied") -> None:
        """Initialize permission denied exception with optional custom message."""
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class NotFoundException(HTTPException):
    """Resource not found exception."""

    def __init__(self, resource: str = "Resource") -> None:
        """Initialize not found exception for specified resource."""
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} not found",
        )


class ValidationException(HTTPException):
    """Validation exception."""

    def __init__(self, detail: str) -> None:
        """Initialize validation exception with error detail."""
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class ConflictException(HTTPException):
    """Conflict exception (e.g., duplicate resource)."""

    def __init__(self, detail: str) -> None:
        """Initialize conflict exception with conflict detail."""
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class NotificationException(HTTPException):
    """Exception during notification sending."""

    def __init__(self, detail: str) -> None:
        """Initialize notification exception with error detail."""
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )
