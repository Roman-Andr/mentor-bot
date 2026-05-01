"""Repository interfaces following Interface Segregation Principle."""

from checklists_service.repositories.interfaces.base import BaseRepository
from checklists_service.repositories.interfaces.certificate import ICertificateRepository
from checklists_service.repositories.interfaces.checklist import IChecklistRepository
from checklists_service.repositories.interfaces.task import ITaskRepository
from checklists_service.repositories.interfaces.template import ITaskTemplateRepository, ITemplateRepository

__all__ = [
    "BaseRepository",
    "ICertificateRepository",
    "IChecklistRepository",
    "ITaskRepository",
    "ITaskTemplateRepository",
    "ITemplateRepository",
]
