"""Unit of Work pattern for transaction management."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Protocol, Self, runtime_checkable

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from feedback_service.repositories.implementations.feedback import (
    CommentRepository,
    ExperienceRatingRepository,
    PulseSurveyRepository,
)
from feedback_service.repositories.implementations.feedback_status_change_history import (
    FeedbackStatusChangeHistoryRepository,
)
from feedback_service.repositories.interfaces.feedback import (
    ICommentRepository,
    IExperienceRatingRepository,
    IPulseSurveyRepository,
)
from feedback_service.repositories.interfaces.feedback_status_change_history import (
    IFeedbackStatusChangeHistoryRepository,
)


@runtime_checkable
class IUnitOfWork(Protocol):
    """Unit of Work interface for managing repositories and transactions."""

    pulse_surveys: IPulseSurveyRepository
    experience_ratings: IExperienceRatingRepository
    comments: ICommentRepository
    feedback_status_change_history: IFeedbackStatusChangeHistoryRepository

    async def commit(self) -> None:
        """Commit all changes made in this unit of work."""
        ...  # pragma: no cover

    async def rollback(self) -> None:
        """Rollback all changes made in this unit of work."""
        ...  # pragma: no cover

    async def __aenter__(self) -> Self:
        """Enter async context manager."""
        ...  # pragma: no cover

    async def __aexit__(self, *args: object) -> None:
        """Exit async context manager."""
        ...  # pragma: no cover


class SqlAlchemyUnitOfWork(IUnitOfWork):
    """SQLAlchemy implementation of Unit of Work."""

    pulse_surveys: PulseSurveyRepository
    experience_ratings: ExperienceRatingRepository
    comments: CommentRepository
    feedback_status_change_history: FeedbackStatusChangeHistoryRepository

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        """Initialize Unit of Work with session factory."""
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    async def __aenter__(self) -> Self:
        """Enter async context manager and initialize repositories."""
        self._session = self._session_factory()
        self.pulse_surveys = PulseSurveyRepository(self._session)
        self.experience_ratings = ExperienceRatingRepository(self._session)
        self.comments = CommentRepository(self._session)
        self.feedback_status_change_history = FeedbackStatusChangeHistoryRepository(self._session)
        logger.debug("UnitOfWork session opened")
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: object
    ) -> None:
        """Exit async context manager and clean up session."""
        if self._session:
            if exc_type:
                logger.warning("UnitOfWork rollback on exception (exc_type={})", exc_type)
                await self._session.rollback()
            await self._session.close()
            self._session = None
            logger.debug("UnitOfWork session closed")

    async def commit(self) -> None:
        """Commit all changes made in this unit of work."""
        if not self._session:
            logger.error("UnitOfWork commit failed: session not initialized")
            msg = "Session not initialized"
            raise RuntimeError(msg)
        await self._session.commit()
        logger.debug("UnitOfWork committed")

    async def rollback(self) -> None:
        """Rollback all changes made in this unit of work."""
        if not self._session:
            logger.error("UnitOfWork rollback failed: session not initialized")
            msg = "Session not initialized"
            raise RuntimeError(msg)
        await self._session.rollback()
        logger.debug("UnitOfWork rolled back")


@asynccontextmanager
async def sqlalchemy_uow(session_factory: async_sessionmaker) -> AsyncGenerator[SqlAlchemyUnitOfWork]:
    """Async context manager for SqlAlchemyUnitOfWork."""
    async with SqlAlchemyUnitOfWork(session_factory) as uow:
        yield uow
