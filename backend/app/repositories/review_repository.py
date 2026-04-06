"""
ReviewRepository for data access - Task 3.1
Requirements: 1, 2, 3, 4, 5
"""
from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review
from app.models.user import User
from app.models.song import Song


class ReviewRepository:
    """Repository for Review data access"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: int,
        song_id: int,
        rating: int,
        body: Optional[str] = None,
        is_flagged: bool = False
    ) -> Review:
        """Create new review"""
        review = Review(
            user_id=user_id,
            song_id=song_id,
            rating=rating,
            body=body,
            is_flagged=is_flagged
        )
        self.db.add(review)
        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def get_by_id(self, review_id: UUID) -> Optional[Review]:
        """Get review by ID"""
        stmt = select(Review).where(Review.id == review_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_and_song(self, user_id: int, song_id: int) -> Optional[Review]:
        """Check if user already reviewed song"""
        stmt = select(Review).where(
            and_(Review.user_id == user_id, Review.song_id == song_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_reviews_for_song(
        self,
        song_id: int,
        page: int = 1,
        page_size: int = 10,
        exclude_flagged: bool = True
    ) -> Tuple[List[Review], int]:
        """Get paginated reviews for a song"""
        # Build base query
        conditions = [Review.song_id == song_id]
        if exclude_flagged:
            conditions.append(Review.is_flagged == False)

        # Count total
        count_stmt = select(func.count()).select_from(Review).where(and_(*conditions))
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0

        # Get paginated results with user info
        offset = (page - 1) * page_size
        stmt = (
            select(Review)
            .options(joinedload(Review.user))
            .where(and_(*conditions))
            .order_by(Review.created_at.desc())
            .limit(page_size)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        reviews = list(result.scalars().all())

        return reviews, total

    async def get_reviews_by_user(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[Review], int]:
        """Get user's reviews with song/artist info"""
        # Count total
        count_stmt = select(func.count()).select_from(Review).where(Review.user_id == user_id)
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0

        # Get paginated results
        offset = (page - 1) * page_size
        stmt = (
            select(Review)
            .options(
                joinedload(Review.song).joinedload(Song.album)
            )
            .where(Review.user_id == user_id)
            .order_by(Review.created_at.desc())
            .limit(page_size)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        reviews = list(result.scalars().all())

        return reviews, total

    async def update(
        self,
        review_id: UUID,
        rating: Optional[int] = None,
        body: Optional[str] = None,
        is_flagged: Optional[bool] = None
    ) -> Optional[Review]:
        """Update review"""
        review = await self.get_by_id(review_id)
        if not review:
            return None

        if rating is not None:
            review.rating = rating
        if body is not None:
            review.body = body
        if is_flagged is not None:
            review.is_flagged = is_flagged

        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def delete(self, review_id: UUID) -> bool:
        """Delete review"""
        review = await self.get_by_id(review_id)
        if not review:
            return False

        await self.db.delete(review)
        await self.db.commit()
        return True

    async def increment_helpful_count(self, review_id: UUID, delta: int) -> None:
        """Increment or decrement helpful_count"""
        review = await self.get_by_id(review_id)
        if review:
            review.helpful_count += delta
            await self.db.commit()

    async def get_flagged_reviews(
        self,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Review], int]:
        """Get flagged reviews (admin)"""
        count_stmt = select(func.count()).select_from(Review).where(Review.is_flagged == True)
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0

        offset = (page - 1) * page_size
        stmt = (
            select(Review)
            .options(joinedload(Review.user), joinedload(Review.song))
            .where(Review.is_flagged == True)
            .order_by(Review.created_at.desc())
            .limit(page_size)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        reviews = list(result.scalars().all())

        return reviews, total
