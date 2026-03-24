"""Attachment management service with repository pattern."""

from knowledge_service.core import NotFoundException
from knowledge_service.core.enums import AttachmentType
from knowledge_service.models import Attachment
from knowledge_service.repositories import IUnitOfWork


class AttachmentService:
    """Service for attachment management operations."""

    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize attachment service with Unit of Work."""
        self._uow = uow

    async def create_attachment(
        self,
        article_id: int,
        name: str,
        attachment_type: AttachmentType,
        url: str,
        file_size: int | None = None,
        mime_type: str | None = None,
        description: str | None = None,
        order: int = 0,
        *,
        is_downloadable: bool = True,
    ) -> Attachment:
        """Create new attachment."""
        attachment = Attachment(
            article_id=article_id,
            name=name,
            type=attachment_type,
            url=url,
            file_size=file_size,
            mime_type=mime_type,
            description=description,
            order=order,
            is_downloadable=is_downloadable,
        )
        created = await self._uow.attachments.create(attachment)
        await self._uow.commit()
        return created

    async def get_attachment(self, attachment_id: int) -> Attachment:
        """Get attachment by ID."""
        attachment = await self._uow.attachments.get_by_id(attachment_id)
        if not attachment:
            msg = "Attachment"
            raise NotFoundException(msg)
        return attachment

    async def get_attachments_by_article(self, article_id: int) -> list[Attachment]:
        """Get all attachments for an article."""
        attachments = await self._uow.attachments.get_by_article(article_id)
        return list(attachments)

    async def delete_attachment(self, attachment_id: int) -> None:
        """Delete attachment."""
        await self.get_attachment(attachment_id)
        await self._uow.attachments.delete(attachment_id)
        await self._uow.commit()
