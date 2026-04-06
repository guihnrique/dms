"""
FeedbackRepository for recommendation tracking - Task 3.5
Requirements: 11
"""
from sqlalchemy import insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recommendation_feedback import RecommendationFeedback


class FeedbackRepository:
    """Repository for recommendation feedback tracking"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_feedback(
        self,
        user_id: int,
        song_id: int,
        action: str
    ) -> None:
        """
        Log recommendation feedback (insert or update)

        Uses INSERT ... ON CONFLICT UPDATE to handle duplicates
        """
        stmt = pg_insert(RecommendationFeedback).values(
            user_id=user_id,
            song_id=song_id,
            action=action
        ).on_conflict_do_update(
            index_elements=['user_id', 'song_id'],
            set_=dict(action=action)
        )

        await self.db.execute(stmt)
        await self.db.commit()

    async def get_user_feedback(self, user_id: int, song_id: int):
        """Get feedback for specific user and song"""
        from sqlalchemy import select
        stmt = select(RecommendationFeedback).where(
            RecommendationFeedback.user_id == user_id,
            RecommendationFeedback.song_id == song_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
