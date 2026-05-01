"""Repository interfaces."""

from escalation_service.repositories.interfaces.base import BaseRepository
from escalation_service.repositories.interfaces.escalation import IEscalationRepository
from escalation_service.repositories.interfaces.escalation_status_history import IEscalationStatusHistoryRepository
from escalation_service.repositories.interfaces.mentor_intervention_history import IMentorInterventionHistoryRepository

__all__ = [
    "BaseRepository",
    "IEscalationRepository",
    "IEscalationStatusHistoryRepository",
    "IMentorInterventionHistoryRepository",
]
