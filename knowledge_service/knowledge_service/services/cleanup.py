"""Cleanup service for old search history records."""

from loguru import logger

from knowledge_service.config import settings
from knowledge_service.database import AsyncSessionLocal
from knowledge_service.repositories import SqlAlchemyUnitOfWork


async def cleanup_old_search_history(retention_days: int | None = None) -> int:
    """Delete search history entries older than retention period.
    
    Args:
        retention_days: Number of days to retain. If None, uses config value.
        
    Returns:
        Number of deleted records.
    """
    if retention_days is None:
        retention_days = settings.SEARCH_HISTORY_RETENTION_DAYS
    
    async with SqlAlchemyUnitOfWork(AsyncSessionLocal) as uow:
        deleted_count = await uow.search_history.delete_old_search_history(retention_days)
        await uow.commit()
        
        logger.info(
            "Cleaned up {} old search history records (retention: {} days)",
            deleted_count,
            retention_days,
        )
        
        return deleted_count
