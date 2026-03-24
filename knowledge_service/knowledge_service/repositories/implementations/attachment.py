"""SQLAlchemy implementation of Attachment repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from knowledge_service.models import Attachment
from knowledge_service.repositories.implementations.base import SqlAlchemyBaseRepository
from knowledge_service.repositories.interfaces.attachment import IAttachmentRepository


class AttachmentRepository(SqlAlchemyBaseRepository[Attachment, int], IAttachmentRepository):
    """SQLAlchemy implementation of Attachment repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize attachment repository."""
        super().__init__(session, Attachment)

    async def get_by_article(self, article_id: int) -> list[Attachment]:
        """Get all attachments for an article, ordered by order field."""
        stmt = (
            select(Attachment)
            .where(Attachment.article_id == article_id)
            .order_by(Attachment.order, Attachment.created_at)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
