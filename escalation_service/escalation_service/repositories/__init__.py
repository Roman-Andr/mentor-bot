"""Repository pattern implementation for data access layer."""

from escalation_service.repositories.implementations import EscalationRepository
from escalation_service.repositories.interfaces import BaseRepository, IEscalationRepository
from escalation_service.repositories.unit_of_work import IUnitOfWork, SqlAlchemyUnitOfWork, sqlalchemy_uow

__all__ = [
    "BaseRepository",
    "EscalationRepository",
    "IEscalationRepository",
    "IUnitOfWork",
    "SqlAlchemyUnitOfWork",
    "sqlalchemy_uow",
]
