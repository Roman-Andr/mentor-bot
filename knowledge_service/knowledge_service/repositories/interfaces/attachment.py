"""Attachment repository interface."""

from abc import abstractmethod
from typing import TYPE_CHECKING

from knowledge_service.models.attachment import Attachment
from knowledge_service.repositories.interfaces.base import BaseRepository

if TYPE_CHECKING:
    pass


class IAttachmentRepository(BaseRepository["Attachment", int]):
    """Attachment repository interface."""

    @abstractmethod
    async def get_by_article(self, article_id: int) -> list[Attachment]:
        """Get all attachments for an article, ordered by order field."""
