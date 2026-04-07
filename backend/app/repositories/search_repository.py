"""
SearchRepository for multi-entity queries - Task 3.1
Requirements: 1, 2, 3, 4
"""
from typing import List, Optional
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.artist import Artist
from app.models.album import Album
from app.models.song import Song


class SearchRepository:
    """Repository for multi-entity search queries"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_artists(self, query: str, limit: int = 50) -> List[dict]:
        """
        Search artists with relevance scoring

        Scoring:
        - Exact match: 100
        - Prefix match: 80
        - Contains: 60
        - Popularity boost from albums_count
        """
        query_lower = query.lower()

        # Relevance scoring with CASE statement
        relevance_score = case(
            (func.lower(Artist.name) == query_lower, 100),
            (func.lower(Artist.name).like(f"{query_lower}%"), 80),
            (func.lower(Artist.name).like(f"%{query_lower}%"), 60),
            else_=0
        )

        # Count albums for popularity boost
        albums_count_subquery = (
            select(func.count(Album.id))
            .where(Album.artist_id == Artist.id)
            .scalar_subquery()
        )

        stmt = (
            select(
                Artist.id,
                Artist.name,
                relevance_score.label("relevance_score"),
                albums_count_subquery.label("albums_count")
            )
            .where(Artist.name.ilike(f"%{query}%"))
            .order_by(relevance_score.desc(), albums_count_subquery.desc())
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        return [
            {
                "id": row.id,
                "name": row.name,
                "relevance_score": row.relevance_score,
                "albums_count": row.albums_count or 0
            }
            for row in rows
        ]

    async def search_albums(
        self,
        query: str,
        genres: Optional[List[str]] = None,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        limit: int = 50
    ) -> List[dict]:
        """
        Search albums with genre and year filtering
        """
        query_lower = query.lower()

        # Relevance scoring
        relevance_score = case(
            (func.lower(Album.title) == query_lower, 100),
            (func.lower(Album.title).like(f"{query_lower}%"), 80),
            (func.lower(Album.title).like(f"%{query_lower}%"), 60),
            else_=0
        )

        stmt = (
            select(
                Album.id,
                Album.title,
                Album.artist_id,
                Artist.name.label("artist_name"),
                Album.release_year,
                Album.genre,
                relevance_score.label("relevance_score")
            )
            .join(Artist, Album.artist_id == Artist.id)
            .where(Album.title.ilike(f"%{query}%"))
        )

        # Apply genre filter (OR logic)
        if genres:
            stmt = stmt.where(Album.genre.in_(genres))

        # Apply year range filter
        if year_min is not None:
            stmt = stmt.where(Album.release_year >= year_min)
        if year_max is not None:
            stmt = stmt.where(Album.release_year <= year_max)

        stmt = stmt.order_by(relevance_score.desc()).limit(limit)

        result = await self.db.execute(stmt)
        rows = result.all()

        return [
            {
                "id": row.id,
                "title": row.title,
                "artist_id": row.artist_id,
                "artist_name": row.artist_name,
                "release_year": row.release_year,
                "genre": row.genre,
                "relevance_score": row.relevance_score
            }
            for row in rows
        ]

    async def search_songs(
        self,
        query: str,
        genres: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[dict]:
        """
        Search songs with genre filtering and soft-delete exclusion
        """
        query_lower = query.lower()

        # Relevance scoring with popularity boost
        base_relevance = case(
            (func.lower(Song.title) == query_lower, 100),
            (func.lower(Song.title).like(f"{query_lower}%"), 80),
            (func.lower(Song.title).like(f"%{query_lower}%"), 60),
            else_=0
        )

        # Popularity boost from review_count (capped at +10)
        popularity_boost = func.least(Song.review_count, 10)
        relevance_score = base_relevance + popularity_boost

        stmt = (
            select(
                Song.id,
                Song.title,
                Artist.name.label("artist_name"),
                Album.title.label("album_title"),
                Song.genre,
                Album.album_cover_url.label("cover_art_url"),
                Song.average_rating,
                Song.review_count,
                relevance_score.label("relevance_score")
            )
            .join(Album, Song.album_id == Album.id)
            .join(Artist, Album.artist_id == Artist.id)
            .where(
                Song.title.ilike(f"%{query}%"),
                Song.deleted_at.is_(None)  # Exclude soft-deleted songs
            )
        )

        # Apply genre filter (OR logic)
        if genres:
            stmt = stmt.where(Song.genre.in_(genres))

        stmt = stmt.order_by(relevance_score.desc()).limit(limit)

        result = await self.db.execute(stmt)
        rows = result.all()

        return [
            {
                "id": row.id,
                "title": row.title,
                "artist_name": row.artist_name,
                "album_title": row.album_title,
                "genre": row.genre,
                "cover_art_url": row.cover_art_url,
                "average_rating": row.average_rating,
                "review_count": row.review_count,
                "relevance_score": min(row.relevance_score, 100)  # Cap at 100
            }
            for row in rows
        ]
