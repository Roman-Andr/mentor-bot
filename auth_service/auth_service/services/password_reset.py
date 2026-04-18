"""Password reset service with secure token handling and rate limiting."""

import hashlib
import logging
import secrets
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import select

from auth_service.core import hash_password
from auth_service.models import PasswordResetToken, User
from auth_service.repositories.unit_of_work import IUnitOfWork

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


logger = logging.getLogger(__name__)


class PasswordResetService:
    """Service for managing password reset operations."""

    TOKEN_EXPIRY_HOURS = 24
    MAX_REQUESTS_PER_HOUR = 3
    TOKEN_LENGTH = 64

    def __init__(self, uow: IUnitOfWork, session: "AsyncSession") -> None:
        """Initialize password reset service with unit of work and session."""
        self._uow = uow
        self._session = session

    @staticmethod
    def _generate_token() -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(PasswordResetService.TOKEN_LENGTH)

    @staticmethod
    def _hash_token(token: str) -> str:
        """Hash a token for secure storage."""
        return hashlib.sha256(token.encode()).hexdigest()

    async def _get_token_record(self, token_hash: str) -> PasswordResetToken | None:
        """Get token record by its hash."""
        stmt = (
            select(PasswordResetToken)
            .where(PasswordResetToken.token_hash == token_hash)
            .where(PasswordResetToken.used_at.is_(None))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def _count_recent_requests(self, user_id: int) -> int:
        """Count password reset requests in the last hour for a user."""
        one_hour_ago = datetime.now(UTC) - timedelta(hours=1)
        stmt = (
            select(PasswordResetToken)
            .where(PasswordResetToken.user_id == user_id)
            .where(PasswordResetToken.created_at >= one_hour_ago)
        )
        result = await self._session.execute(stmt)
        return len(result.scalars().all())

    async def request_reset(
        self,
        email: str,
        ip_address: str | None = None,
    ) -> tuple[bool, str | None, User | None]:
        """Request a password reset for a user.

        Args:
            email: User's email address
            ip_address: Optional IP address for rate limiting tracking

        Returns:
            Tuple of (success, raw_token, user). raw_token is None if rate limited or user not found.
            Always returns success=True to prevent email enumeration, but token may be None.
        """
        # Find user by email
        user = await self._uow.users.get_by_email(email)
        if not user:
            # Return success=True to prevent email enumeration
            logger.info("Password reset requested for non-existent email: %s", email)
            return True, None, None

        if not user.is_active:
            logger.info("Password reset requested for inactive user: %s", user.id)
            return True, None, None

        # Check rate limit
        recent_requests = await self._count_recent_requests(user.id)
        if recent_requests >= self.MAX_REQUESTS_PER_HOUR:
            logger.warning(
                "Rate limit exceeded for password reset - user_id: %s, ip: %s",
                user.id,
                ip_address,
            )
            return True, None, None

        # Generate token and hash
        raw_token = self._generate_token()
        token_hash = self._hash_token(raw_token)

        # Create token record
        expires_at = datetime.now(UTC) + timedelta(hours=self.TOKEN_EXPIRY_HOURS)
        token_record = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            ip_address=ip_address,
        )

        self._session.add(token_record)
        await self._session.flush()

        logger.info("Password reset token created for user: %s", user.id)
        return True, raw_token, user

    async def validate_token(self, token: str) -> User | None:
        """Validate a password reset token.

        Args:
            token: The raw token to validate

        Returns:
            User if token is valid and not expired, None otherwise
        """
        token_hash = self._hash_token(token)
        token_record = await self._get_token_record(token_hash)

        if not token_record:
            logger.debug("Token not found or already used")
            return None

        # Check expiration
        if datetime.now(UTC) > token_record.expires_at:
            logger.debug("Token expired")
            return None

        # Get user
        user = await self._uow.users.get_by_id(token_record.user_id)
        if not user or not user.is_active:
            logger.debug("User not found or inactive")
            return None

        return user

    async def confirm_reset(self, token: str, new_password: str) -> bool:
        """Confirm password reset with a valid token.

        Args:
            token: The raw reset token
            new_password: The new password to set

        Returns:
            True if password was successfully reset, False otherwise
        """
        token_hash = self._hash_token(token)
        token_record = await self._get_token_record(token_hash)

        if not token_record:
            logger.warning("Confirm reset failed: token not found or already used")
            return False

        # Check expiration
        if datetime.now(UTC) > token_record.expires_at:
            logger.warning("Confirm reset failed: token expired")
            return False

        # Get user
        user = await self._uow.users.get_by_id(token_record.user_id)
        if not user or not user.is_active:
            logger.warning("Confirm reset failed: user not found or inactive")
            return False

        # Update password
        user.password_hash = hash_password(new_password)
        user.updated_at = datetime.now(UTC)

        # Mark token as used
        token_record.used_at = datetime.now(UTC)

        await self._session.flush()

        logger.info("Password reset successful for user: %s", user.id)
        return True
