"""Background scheduler for processing scheduled notifications."""

import asyncio
import logging

from notification_service.config import settings
from notification_service.database import AsyncSessionLocal
from notification_service.repositories.unit_of_work import SqlAlchemyUnitOfWork
from notification_service.services.notification import NotificationService

logger = logging.getLogger(__name__)


class Scheduler:
    """Background scheduler that periodically processes scheduled notifications."""

    def __init__(self, poll_interval: int = 60) -> None:
        """Initialize scheduler with poll interval in seconds."""
        self.poll_interval = poll_interval
        self._running = False
        self._task: asyncio.Task | None = None

    async def run(self) -> None:
        """Start the scheduler loop."""
        self._running = True
        logger.info(f"Scheduler started with poll interval {self.poll_interval}s")
        while self._running:
            try:
                await self._process()
            except Exception as e:
                logger.exception(f"Error in scheduler loop: {e}")
            await asyncio.sleep(self.poll_interval)

    async def stop(self) -> None:
        """Stop the scheduler loop."""
        self._running = False
        if self._task:
            self._task.cancel()
        logger.info("Scheduler stopped")

    async def _process(self) -> None:
        """Process due scheduled notifications."""
        async with SqlAlchemyUnitOfWork(AsyncSessionLocal) as uow:
            service = NotificationService(uow)
            sent = await service.process_scheduled()
            if sent:
                logger.info(f"Processed {len(sent)} scheduled notifications")


# Global scheduler instance
scheduler = Scheduler(poll_interval=settings.SCHEDULER_POLL_INTERVAL_SECONDS)
