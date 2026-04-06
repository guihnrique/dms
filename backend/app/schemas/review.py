"""
Pydantic schemas for review endpoints - Task 2.1, 2.2
Request and response validation schemas
Requirements: 1, 4, 5, 11, 12
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal
from datetime import datetime
from uuid import UUID


class ReviewCreateRequest(BaseModel):
    """Request schema for creating/updating a review"""
    song_id: int = Field(..., description="Song ID to review")
    rating: int = Field(..., ge=1, le=5, description="Rating (1-5)")
    body: Optional[str] = Field(None, max_length=2000, description="Review text (max 2000 chars)")

    @field_validator('body')
    @classmethod
    def validate_body(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v


class ReviewUpdateRequest(BaseModel):
    """Request schema for updating a review"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    body: Optional[str] = Field(None, max_length=2000)

    @field_validator('body')
    @classmethod
    def validate_body(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v


class VoteRequest(BaseModel):
    """Request schema for voting on review helpfulness"""
    vote_type: Literal["helpful", "not_helpful"] = Field(..., description="Vote type")


class ReviewResponse(BaseModel):
    """Response schema for a review"""
    id: UUID
    user_id: int
    username: str
    song_id: int
    rating: int
    body: Optional[str]
    is_flagged: bool
    helpful_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewListResponse(BaseModel):
    """Response schema for paginated reviews list"""
    items: List[ReviewResponse]
    total: int
    page: int
    page_size: int


class SongWithReviewsResponse(BaseModel):
    """Response schema for song with review data"""
    id: int
    title: str
    average_rating: Optional[float]
    review_count: int
    user_review: Optional[ReviewResponse] = None
    review_status: str  # "reviewed" or "not_reviewed"

    class Config:
        from_attributes = True
