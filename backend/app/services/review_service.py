"""
ReviewService for business logic - Task 5
Requirements: 1, 2, 3, 6, 8, 10
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException

from app.repositories.review_repository import ReviewRepository
from app.repositories.vote_repository import VoteRepository
from app.repositories.song_repository import SongRepository
from app.services.moderation_service import ModerationService
from app.models.review import Review


class ReviewService:
    """Service for review business logic"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.review_repo = ReviewRepository(db)
        self.song_repo = SongRepository(db)
        self.moderation = ModerationService()

    async def create_or_update_review(
        self,
        user_id: int,
        song_id: int,
        rating: int,
        body: Optional[str] = None
    ) -> tuple[Review, str]:
        """
        Create or update review (one per user per song)
        Returns: (review, message)
        """
        # Validate song exists
        song = await self.song_repo.get_by_id(song_id)
        if not song:
            raise HTTPException(status_code=400, detail="Song not found")

        # Check for existing review
        existing = await self.review_repo.get_by_user_and_song(user_id, song_id)

        # Check profanity
        is_flagged = False
        if body:
            is_flagged = self.moderation.check_profanity(body)

        if existing:
            # Update existing
            updated = await self.review_repo.update(
                existing.id,
                rating=rating,
                body=body,
                is_flagged=is_flagged
            )
            await self.recalculate_average_rating(song_id)
            return updated, "You have already reviewed this song. Your review has been updated."
        else:
            # Create new
            review = await self.review_repo.create(
                user_id=user_id,
                song_id=song_id,
                rating=rating,
                body=body,
                is_flagged=is_flagged
            )
            await self.recalculate_average_rating(song_id)
            return review, "Review created successfully"

    async def recalculate_average_rating(self, song_id: int) -> None:
        """Recalculate and update song's average rating"""
        # Query all non-flagged reviews
        stmt = select(
            func.avg(Review.rating),
            func.count(Review.id)
        ).where(
            Review.song_id == song_id,
            Review.is_flagged == False
        )
        result = await self.db.execute(stmt)
        avg_rating, count = result.one()

        # Update song
        if count > 0:
            # Round to 1 decimal
            avg_rating = round(float(avg_rating), 1)
            await self.song_repo.update_average_rating(song_id, avg_rating, count)
        else:
            # No reviews
            await self.song_repo.update_average_rating(song_id, None, 0)

    async def delete_review(self, review_id: UUID) -> bool:
        """Delete review and recalculate rating"""
        review = await self.review_repo.get_by_id(review_id)
        if not review:
            return False

        song_id = review.song_id
        deleted = await self.review_repo.delete(review_id)

        if deleted:
            await self.recalculate_average_rating(song_id)

        return deleted


class VotingService:
    """Service for helpfulness voting"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.review_repo = ReviewRepository(db)
        self.vote_repo = VoteRepository(db)

    async def vote(
        self,
        user_id: int,
        review_id: UUID,
        vote_type: str
    ) -> None:
        """Cast or update vote on review"""
        # Get review
        review = await self.review_repo.get_by_id(review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")

        # Prevent voting on own review
        if review.user_id == user_id:
            raise HTTPException(status_code=400, detail="Cannot vote on your own review")

        # Check existing vote
        existing_vote = await self.vote_repo.get_vote(user_id, review_id)

        if existing_vote:
            if existing_vote.vote_type == vote_type:
                raise HTTPException(status_code=400, detail="You already voted this way")

            # Vote changed - adjust count
            old_was_helpful = existing_vote.vote_type == "helpful"
            new_is_helpful = vote_type == "helpful"

            if old_was_helpful and not new_is_helpful:
                # helpful -> not_helpful: decrement
                await self.review_repo.increment_helpful_count(review_id, -1)
            elif not old_was_helpful and new_is_helpful:
                # not_helpful -> helpful: increment
                await self.review_repo.increment_helpful_count(review_id, 1)

            # Update vote
            await self.vote_repo.create_or_update_vote(user_id, review_id, vote_type)
        else:
            # New vote
            await self.vote_repo.create_or_update_vote(user_id, review_id, vote_type)

            # Increment if helpful
            if vote_type == "helpful":
                await self.review_repo.increment_helpful_count(review_id, 1)
