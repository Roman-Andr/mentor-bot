"""Repository interfaces."""

from escalation_service.repositories.interfaces.base import BaseRepository
from escalation_service.repositories.interfaces.escalation import IEscalationRepository

__all__ = [
    "BaseRepository",
    "IEscalationRepository",
]
