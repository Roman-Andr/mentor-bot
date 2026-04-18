"""Notification template repository interface."""

from abc import abstractmethod
from collections.abc import Sequence

from notification_service.models import NotificationTemplate
from notification_service.repositories.interfaces.base import BaseRepository


class INotificationTemplateRepository(BaseRepository["NotificationTemplate", int]):
    """Notification template repository interface."""

    @abstractmethod
    async def get_by_name_channel_language(
        self, name: str, channel: str, language: str = "en"
    ) -> NotificationTemplate | None:
        """Get active template by name, channel, and language."""

    @abstractmethod
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

    @abstractmethod
    async def get_all_versions(self, name: str, channel: str, language: str) -> Sequence[NotificationTemplate]:
        """Get all versions of a template (including inactive)."""
