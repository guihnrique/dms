"""
Review API routes - Task 7
Requirements: 1, 2, 3, 4, 5, 7, 9
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.review import verify_review_ownership
from app.dependencies.rbac import require_role
from app.models.user import User, UserRole
from app.models.review import Review
from app.services.review_service import ReviewService, VotingService
from app.repositories.review_repository import ReviewRepository
from app.schemas.review import (
    ReviewCreateRequest,
    ReviewUpdateRequest,
    VoteRequest,
    ReviewResponse,
    ReviewListResponse
)

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    request: ReviewCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create or update review (one per user per song)"""
    service = ReviewService(db)
    review, message = await service.create_or_update_review(
        user_id=current_user.id,
        song_id=request.song_id,
        rating=request.rating,
        body=request.body
    )

    # Add username to response
    response = ReviewResponse(
        id=review.id,
        user_id=review.user_id,
        username=current_user.email.split('@')[0],
        song_id=review.song_id,
        rating=review.rating,
        body=review.body,
        is_flagged=review.is_flagged,
        helpful_count=review.helpful_count,
        created_at=review.created_at,
        updated_at=review.updated_at
    )

    return response


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: UUID,
    request: ReviewUpdateRequest,
    review: Review = Depends(verify_review_ownership),
    db: AsyncSession = Depends(get_db)
):
    """Update review (owner only)"""
    service = ReviewService(db)
    repo = ReviewRepository(db)

    # Update fields
    updated = await repo.update(
        review_id,
        rating=request.rating,
        body=request.body
    )

    # Recalculate rating
    await service.recalculate_average_rating(updated.song_id)

    response = ReviewResponse(
        id=updated.id,
        user_id=updated.user_id,
        username=updated.user.email.split('@')[0],
        song_id=updated.song_id,
        rating=updated.rating,
        body=updated.body,
        is_flagged=updated.is_flagged,
        helpful_count=updated.helpful_count,
        created_at=updated.created_at,
        updated_at=updated.updated_at
    )

    return response


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: UUID,
    review: Review = Depends(verify_review_ownership),
    db: AsyncSession = Depends(get_db)
):
    """Delete review (owner only)"""
    service = ReviewService(db)
    await service.delete_review(review_id)
    return None


@router.get("/songs/{song_id}/reviews", response_model=ReviewListResponse)
async def get_song_reviews(
    song_id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get reviews for a song (public, excludes flagged)"""
    repo = ReviewRepository(db)
    reviews, total = await repo.get_reviews_for_song(
        song_id,
        page=page,
        page_size=page_size,
        exclude_flagged=True
    )

    items = [
        ReviewResponse(
            id=r.id,
            user_id=r.user_id,
            username=r.user.email.split('@')[0],
            song_id=r.song_id,
            rating=r.rating,
            body=r.body,
            is_flagged=r.is_flagged,
            helpful_count=r.helpful_count,
            created_at=r.created_at,
            updated_at=r.updated_at
        )
        for r in reviews
    ]

    return ReviewListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/me", response_model=ReviewListResponse)
async def get_my_reviews(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's reviews"""
    repo = ReviewRepository(db)
    reviews, total = await repo.get_reviews_by_user(
        current_user.id,
        page=page,
        page_size=page_size
    )

    items = [
        ReviewResponse(
            id=r.id,
            user_id=r.user_id,
            username=current_user.email.split('@')[0],
            song_id=r.song_id,
            rating=r.rating,
            body=r.body,
            is_flagged=r.is_flagged,
            helpful_count=r.helpful_count,
            created_at=r.created_at,
            updated_at=r.updated_at
        )
        for r in reviews
    ]

    return ReviewListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/{review_id}/vote", status_code=status.HTTP_200_OK)
async def vote_on_review(
    review_id: UUID,
    request: VoteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Vote on review helpfulness"""
    service = VotingService(db)
    await service.vote(current_user.id, review_id, request.vote_type)
    return {"message": "Vote recorded"}


# Admin endpoints
@router.get("/admin/flagged", response_model=ReviewListResponse)
async def get_flagged_reviews(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Get flagged reviews (admin only)"""
    repo = ReviewRepository(db)
    reviews, total = await repo.get_flagged_reviews(page, page_size)

    items = [
        ReviewResponse(
            id=r.id,
            user_id=r.user_id,
            username=r.user.email.split('@')[0],
            song_id=r.song_id,
            rating=r.rating,
            body=r.body,
            is_flagged=r.is_flagged,
            helpful_count=r.helpful_count,
            created_at=r.created_at,
            updated_at=r.updated_at
        )
        for r in reviews
    ]

    return ReviewListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/admin/{review_id}/approve")
async def approve_review(
    review_id: UUID,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Approve flagged review (admin only)"""
    repo = ReviewRepository(db)
    await repo.update(review_id, is_flagged=False)
    return {"message": "Review approved"}


@router.delete("/admin/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_review(
    review_id: UUID,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Delete review (admin)"""
    service = ReviewService(db)
    await service.delete_review(review_id)
    return None
