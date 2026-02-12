"""Attachment management service."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from knowledge_service.core import NotFoundException
from knowledge_service.core.enums import AttachmentType
from knowledge_service.models import Attachment


class AttachmentService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_attachment(
        self,
        article_id: int,
        name: str,
        type: AttachmentType,
        url: str,
        file_size: int | None = None,
        mime_type: str | None = None,
        description: str | None = None,
        order: int = 0,
        is_downloadable: bool = True,
    ) -> Attachment:
        attachment = Attachment(
            article_id=article_id,
            name=name,
            type=type,
            url=url,
            file_size=file_size,
            mime_type=mime_type,
            description=description,
            order=order,
            is_downloadable=is_downloadable,
        )
        self.db.add(attachment)
        await self.db.commit()
        await self.db.refresh(attachment)
        return attachment

    async def get_attachment(self, attachment_id: int) -> Attachment:
        stmt = select(Attachment).where(Attachment.id == attachment_id)
        result = await self.db.execute(stmt)
        attachment = result.scalar_one_or_none()
        if not attachment:
            msg = "Attachment"
            raise NotFoundException(msg)
        return attachment

    async def delete_attachment(self, attachment_id: int) -> None:
        attachment = await self.get_attachment(attachment_id)
        await self.db.delete(attachment)
        await self.db.commit()
