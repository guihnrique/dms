"""
SearchService for multi-entity orchestration - Tasks 4.1-4.3
Requirements: 1, 2, 3, 4, 5, 12
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.search_repository import SearchRepository
from app.schemas.search import (
    SearchResponse,
    ArtistResult,
    AlbumResult,
    SongResult,
    SortParameter,
    SortOrder
)


class SearchService:
    """Service for multi-entity search orchestration"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SearchRepository(db)

    async def search(
        self,
        query: str,
        genres: Optional[List[str]] = None,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        sort_by: SortParameter = SortParameter.RELEVANCE,
        sort_order: SortOrder = SortOrder.DESC
    ) -> SearchResponse:
        """
        Execute multi-entity search with filtering and sorting

        Args:
            query: Search query (min 2 characters)
            genres: Filter by genres (OR logic)
            year_min: Minimum release year (1900 to current_year + 1)
            year_max: Maximum release year (1900 to current_year + 1)
            sort_by: Sort parameter (relevance, popularity, release_date, rating)
            sort_order: Sort order (asc or desc)

        Returns:
            SearchResponse with grouped results

        Raises:
            ValueError: If query < 2 chars or invalid year range
        """
        # Validate query length
        if len(query) < 2:
            raise ValueError("Search query must be at least 2 characters")

        # Validate year range
        current_year = datetime.now().year
        if year_min is not None and year_min < 1900:
            raise ValueError("year_min must be >= 1900")
        if year_max is not None and year_max > current_year + 1:
            raise ValueError(f"year_max cannot exceed {current_year + 1}")
        if year_min is not None and year_max is not None and year_min > year_max:
            raise ValueError("year_min cannot be greater than year_max")

        # Execute parallel queries
        artists_data = await self.repo.search_artists(query, limit=50)
        albums_data = await self.repo.search_albums(
            query,
            genres=genres,
            year_min=year_min,
            year_max=year_max,
            limit=50
        )
        songs_data = await self.repo.search_songs(
            query,
            genres=genres,
            limit=50
        )

        # Apply custom sorting
        if sort_by != SortParameter.RELEVANCE:
            songs_data = self._apply_sort(songs_data, sort_by, sort_order)
            albums_data = self._apply_sort(albums_data, sort_by, sort_order)

        # Convert to response schemas
        artists = [ArtistResult(**artist) for artist in artists_data]
        albums = [AlbumResult(**album) for album in albums_data]
        songs = [SongResult(**song) for song in songs_data]

        total_count = len(artists) + len(albums) + len(songs)

        return SearchResponse(
            artists=artists,
            albums=albums,
            songs=songs,
            total_count=total_count
        )

    def _apply_sort(
        self,
        results: List[dict],
        sort_by: SortParameter,
        sort_order: SortOrder
    ) -> List[dict]:
        """
        Apply custom sorting to results

        Args:
            results: List of result dictionaries
            sort_by: Sort parameter (popularity, release_date, rating)
            sort_order: Sort direction (asc or desc)

        Returns:
            Sorted list of results
        """
        reverse = (sort_order == SortOrder.DESC)

        if sort_by == SortParameter.POPULARITY:
            # Sort by review_count (for songs) or albums_count (for artists)
            key = lambda x: x.get('review_count', x.get('albums_count', 0))
        elif sort_by == SortParameter.RELEASE_DATE:
            # Sort by release_year (for albums)
            key = lambda x: x.get('release_year', 0) or 0
        elif sort_by == SortParameter.RATING:
            # Sort by average_rating (for songs)
            key = lambda x: float(x.get('average_rating', 0) or 0)
        else:
            # Default to relevance_score
            key = lambda x: x.get('relevance_score', 0)

        return sorted(results, key=key, reverse=reverse)
