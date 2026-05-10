"""SQLAlchemy implementation of Password reset token repository."""

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.models import PasswordResetToken
from auth_service.repositories.implementations.base import SqlAlchemyBaseRepository
from auth_service.repositories.interfaces.password_reset import IPasswordResetRepository


class PasswordResetRepository(SqlAlchemyBaseRepository[PasswordResetToken, int], IPasswordResetRepository):
    """SQLAlchemy implementation of Password reset token repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize PasswordResetRepository with database session."""
        super().__init__(session, PasswordResetToken)

    async def delete_by_user_id(self, user_id: int) -> int:
        """Delete all password reset tokens for a user."""
        stmt = delete(PasswordResetToken).where(PasswordResetToken.user_id == user_id)
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount
