"""
VoteRepository for helpfulness voting - Task 3.2
Requirements: 7
"""
from typing import Optional
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import ReviewVote


class VoteRepository:
    """Repository for ReviewVote data access"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_vote(self, user_id: int, review_id: UUID) -> Optional[ReviewVote]:
        """Get existing vote"""
        stmt = select(ReviewVote).where(
            and_(ReviewVote.user_id == user_id, ReviewVote.review_id == review_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_or_update_vote(
        self,
        user_id: int,
        review_id: UUID,
        vote_type: str
    ) -> ReviewVote:
        """Create new vote or update existing"""
        # Check for existing vote
        existing = await self.get_vote(user_id, review_id)

        if existing:
            # Update existing vote
            existing.vote_type = vote_type
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            # Create new vote
            vote = ReviewVote(
                user_id=user_id,
                review_id=review_id,
                vote_type=vote_type
            )
            self.db.add(vote)
            await self.db.commit()
            await self.db.refresh(vote)
            return vote

    async def get_user_votes_for_reviews(
        self,
        user_id: int,
        review_ids: list[UUID]
    ) -> dict[UUID, str]:
        """Get user's votes for multiple reviews"""
        if not review_ids:
            return {}

        stmt = select(ReviewVote).where(
            and_(
                ReviewVote.user_id == user_id,
                ReviewVote.review_id.in_(review_ids)
            )
        )
        result = await self.db.execute(stmt)
        votes = result.scalars().all()

        return {vote.review_id: vote.vote_type for vote in votes}
