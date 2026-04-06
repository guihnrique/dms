"""
Review dependencies - Task 6.1
Requirements: 9
"""
from uuid import UUID
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.review import Review
from app.repositories.review_repository import ReviewRepository


async def verify_review_ownership(
    review_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Review:
    """
    Verify review ownership

    Returns:
        Review if user is owner

    Raises:
        HTTPException: 404 if not found, 403 if not owner
    """
    repo = ReviewRepository(db)
    review = await repo.get_by_id(review_id)

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not own this review")

    return review
