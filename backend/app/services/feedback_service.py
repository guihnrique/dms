"""
FeedbackService for user actions - Task 7.1
Requirements: 11
"""
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.repositories.feedback_repository import FeedbackRepository


class FeedbackService:
    """Service for recommendation feedback tracking"""

    VALID_ACTIONS = {'accepted', 'dismissed', 'clicked'}

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = FeedbackRepository(db)

    async def log_feedback(
        self,
        user_id: int,
        song_id: int,
        action: str
    ) -> dict:
        """
        Log user feedback on recommendation

        Args:
            user_id: User ID
            song_id: Song ID
            action: User action (accepted, dismissed, clicked)

        Returns:
            Success message

        Raises:
            HTTPException: 400 if invalid action
        """
        # Validate action
        if action not in self.VALID_ACTIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action. Must be one of: {', '.join(self.VALID_ACTIONS)}"
            )

        # Log feedback (insert or update)
        await self.repo.log_feedback(user_id, song_id, action)

        return {"message": "Feedback recorded successfully"}
