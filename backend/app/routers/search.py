"""
Search and Recommendation API routes - Tasks 8.1-8.6
Requirements: 1, 2, 3, 4, 5, 6, 11
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user, get_current_user_optional
from app.models.user import User
from app.services.search_service import SearchService
from app.services.recommendation_service import RecommendationService
from app.services.analytics_service import AnalyticsService
from app.services.feedback_service import FeedbackService
from app.schemas.search import (
    SearchResponse,
    RecommendationResponse,
    FeedbackRequest,
    GenreEnum,
    SortParameter,
    SortOrder
)

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=2, description="Search query"),
    genres: Optional[List[GenreEnum]] = Query(default=None, description="Filter by genres"),
    year_min: Optional[int] = Query(default=None, ge=1900, description="Minimum release year"),
    year_max: Optional[int] = Query(default=None, description="Maximum release year"),
    sort_by: SortParameter = Query(default=SortParameter.RELEVANCE, description="Sort by parameter"),
    sort_order: SortOrder = Query(default=SortOrder.DESC, description="Sort order"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Multi-entity search across artists, albums, and songs

    Supports:
    - Case-insensitive partial matching
    - Genre filtering (OR logic with multiple selection)
    - Year range filtering on albums (inclusive)
    - Custom sorting (relevance, popularity, release_date, rating)
    - Relevance ranking (exact > prefix > contains)

    Query requirements:
    - Minimum 2 characters
    - Year range: 1900 to current_year + 1
    """
    try:
        # Initialize services
        search_service = SearchService(db)
        analytics_service = AnalyticsService(db)

        # Convert GenreEnum to strings
        genre_strings = [g.value for g in genres] if genres else None

        # Execute search
        results = await search_service.search(
            query=q,
            genres=genre_strings,
            year_min=year_min,
            year_max=year_max,
            sort_by=sort_by,
            sort_order=sort_order
        )

        # Log search (non-blocking, PII-aware)
        user_id = current_user.id if current_user else None
        await analytics_service.log_search(q, results.total_count, user_id)

        return results

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    limit: int = Query(default=20, ge=1, le=100, description="Number of recommendations"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized recommendations (authenticated users only)

    Features:
    - Analyzes user's playlists and reviews to build profile
    - Scores candidates based on favorite genres, artists, ratings
    - Caches recommendations for 24 hours (Redis)
    - Fallback to popular songs for users with insufficient data (<3 playlists and <3 reviews)
    - Timeout protection (1-second limit with fallback)

    Scoring weights:
    - Genre match: 40%
    - Artist match: 30%
    - High rating: 20%
    - Popularity: 10%
    """
    from app.dependencies.redis import get_redis_client

    redis_client = await get_redis_client()
    service = RecommendationService(db, redis_client)

    return await service.get_recommendations(current_user.id, limit)


@router.post("/recommendations/feedback", status_code=status.HTTP_200_OK)
async def log_feedback(
    request: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Log user feedback on recommendations (authenticated users only)

    Actions:
    - accepted: User added song to playlist
    - dismissed: User dismissed recommendation
    - clicked: User clicked on recommendation

    Feedback is used to improve future recommendations.
    """
    service = FeedbackService(db)
    return await service.log_feedback(
        user_id=current_user.id,
        song_id=request.song_id,
        action=request.action
    )
