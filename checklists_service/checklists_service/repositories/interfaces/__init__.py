"""Repository interfaces following Interface Segregation Principle."""

from checklists_service.repositories.interfaces.base import BaseRepository
from checklists_service.repositories.interfaces.certificate import ICertificateRepository
from checklists_service.repositories.interfaces.checklist import IChecklistRepository
from checklists_service.repositories.interfaces.checklist_status_history import IChecklistStatusHistoryRepository
from checklists_service.repositories.interfaces.task import ITaskRepository
from checklists_service.repositories.interfaces.task_completion_history import ITaskCompletionHistoryRepository
from checklists_service.repositories.interfaces.template import ITaskTemplateRepository, ITemplateRepository
from checklists_service.repositories.interfaces.template_change_history import ITemplateChangeHistoryRepository

__all__ = [
    "BaseRepository",
    "ICertificateRepository",
    "IChecklistRepository",
    "IChecklistStatusHistoryRepository",
    "ITaskCompletionHistoryRepository",
    "ITaskRepository",
    "ITaskTemplateRepository",
    "ITemplateChangeHistoryRepository",
    "ITemplateRepository",
]
