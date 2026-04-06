"""
AnalyticsService with PII sanitization - Task 5.1
Requirements: 12
"""
import re
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.analytics_repository import AnalyticsRepository

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for analytics with PII protection"""

    # PII detection patterns
    EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    PHONE_PATTERN = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')
    SSN_PATTERN = re.compile(r'\b\d{3}[-]?\d{2}[-]?\d{4}\b')

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AnalyticsRepository(db)

    async def log_search(
        self,
        query_text: str,
        result_count: int,
        user_id: Optional[int] = None
    ) -> None:
        """
        Log search query with PII detection

        Skip logging if PII detected (email, phone, SSN)

        Args:
            query_text: Search query
            result_count: Number of results returned
            user_id: User ID (nullable for guest searches)
        """
        # Check for PII
        if self.contains_pii(query_text):
            logger.warning(f"Skipping search log - PII detected in query")
            return

        # Log non-PII query
        await self.repo.log_search(query_text, result_count, user_id)

        # Log zero-result searches for quality improvement
        if result_count == 0:
            logger.info(f"Zero-result search logged: {query_text}")

    def contains_pii(self, text: str) -> bool:
        """
        Check if text contains PII patterns

        Detects:
        - Email addresses (@ symbol)
        - Phone numbers (XXX-XXX-XXXX format)
        - SSN (XXX-XX-XXXX format)

        Returns:
            True if PII detected, False otherwise
        """
        if not text:
            return False

        # Check for email
        if self.EMAIL_PATTERN.search(text):
            return True

        # Check for phone number
        if self.PHONE_PATTERN.search(text):
            return True

        # Check for SSN
        if self.SSN_PATTERN.search(text):
            return True

        return False
