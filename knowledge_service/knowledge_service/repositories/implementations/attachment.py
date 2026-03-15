"""SQLAlchemy implementation of Attachment repository."""

from sqlalchemy.ext.asyncio import AsyncSession

from knowledge_service.models import Attachment
from knowledge_service.repositories.implementations.base import SqlAlchemyBaseRepository
from knowledge_service.repositories.interfaces.attachment import IAttachmentRepository


class AttachmentRepository(SqlAlchemyBaseRepository[Attachment, int], IAttachmentRepository):
    """SQLAlchemy implementation of Attachment repository."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Attachment)
