"""Password reset token repository interface."""

from abc import abstractmethod

from auth_service.repositories.interfaces.base import BaseRepository


class IPasswordResetRepository(BaseRepository["PasswordResetToken", int]):
    """Password reset token repository interface."""

    @abstractmethod
    async def delete_by_user_id(self, user_id: int) -> int:
        """Delete all password reset tokens for a user. Returns number of deleted records."""
