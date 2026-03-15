"""Attachment repository interface."""


from knowledge_service.repositories.interfaces.base import BaseRepository


class IAttachmentRepository(BaseRepository["Attachment", int]):
    """Attachment repository interface."""
