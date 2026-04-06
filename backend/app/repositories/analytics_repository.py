"""
AnalyticsRepository for search logging - Task 3.4
Requirements: 12
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.models.search_log import SearchLog

logger = logging.getLogger(__name__)


class AnalyticsRepository:
    """Repository for search analytics logging"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_search(
        self,
        query_text: str,
        result_count: int,
        user_id: Optional[int] = None
    ) -> bool:
        """
        Log search query for analytics

        Args:
            query_text: Search query
            result_count: Number of results returned
            user_id: User ID (nullable for guest searches)

        Returns:
            True if logged successfully, False otherwise
        """
        try:
            log_entry = SearchLog(
                query_text=query_text,
                result_count=result_count,
                user_id=user_id
            )
            self.db.add(log_entry)
            await self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to log search: {e}")
            # Non-blocking: don't raise exception
            await self.db.rollback()
            return False
