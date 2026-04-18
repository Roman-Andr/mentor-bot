"""SQLAlchemy implementation of notification template repository."""

from collections.abc import Sequence
from typing import cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.models import NotificationTemplate
from notification_service.repositories.implementations.base import SqlAlchemyBaseRepository
from notification_service.repositories.interfaces.template import INotificationTemplateRepository


class NotificationTemplateRepository(
    SqlAlchemyBaseRepository[NotificationTemplate, int], INotificationTemplateRepository
):
    """SQLAlchemy implementation of NotificationTemplate repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize NotificationTemplateRepository with database session."""
        super().__init__(session, NotificationTemplate)

    async def get_by_name_channel_language(
        self, name: str, channel: str, language: str = "en"
    ) -> NotificationTemplate | None:
        """Get active template by name, channel, and language."""
        stmt = (
            select(NotificationTemplate)
            .where(
                NotificationTemplate.name == name,
                NotificationTemplate.channel == channel,
                NotificationTemplate.language == language,
                NotificationTemplate.is_active == True,  # noqa: E712
            )
            .order_by(NotificationTemplate.version.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_templates(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        name: str | None = None,
        channel: str | None = None,
        language: str | None = None,
        is_active: bool | None = None,
    ) -> tuple[Sequence[NotificationTemplate], int]:
        """Find templates with filtering and return results with total count."""
        count_stmt = select(func.count(NotificationTemplate.id))
        stmt = select(NotificationTemplate)

        # Build filter conditions
        if name:
            stmt = stmt.where(NotificationTemplate.name.ilike(f"%{name}%"))
            count_stmt = count_stmt.where(NotificationTemplate.name.ilike(f"%{name}%"))
        if channel:
            stmt = stmt.where(NotificationTemplate.channel == channel)
            count_stmt = count_stmt.where(NotificationTemplate.channel == channel)
        if language:
            stmt = stmt.where(NotificationTemplate.language == language)
            count_stmt = count_stmt.where(NotificationTemplate.language == language)
        if is_active is not None:
            stmt = stmt.where(NotificationTemplate.is_active == is_active)
            count_stmt = count_stmt.where(NotificationTemplate.is_active == is_active)

        total_result = await self._session.execute(count_stmt)
        total = cast("int", total_result.scalar_one())

        stmt = stmt.order_by(NotificationTemplate.name, NotificationTemplate.channel, NotificationTemplate.language)
        stmt = stmt.offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        templates = result.scalars().all()

        return templates, total

    async def get_all_versions(self, name: str, channel: str, language: str) -> Sequence[NotificationTemplate]:
        """Get all versions of a template (including inactive)."""
        stmt = (
            select(NotificationTemplate)
            .where(
                NotificationTemplate.name == name,
                NotificationTemplate.channel == channel,
                NotificationTemplate.language == language,
            )
            .order_by(NotificationTemplate.version.desc())
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()
