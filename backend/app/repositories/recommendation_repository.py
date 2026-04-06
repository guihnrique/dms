"""
RecommendationRepository for user profile and candidate retrieval - Tasks 3.2-3.3
Requirements: 6, 8
"""
from typing import List, Optional, Set
from sqlalchemy import select, func, union
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.playlist import Playlist, PlaylistSong
from app.models.review import Review
from app.models.song import Song
from app.models.album import Album
from app.models.artist import Artist
from app.schemas.search import UserProfile


class RecommendationRepository:
    """Repository for recommendation data extraction"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def build_user_profile(self, user_id: int) -> UserProfile:
        """
        Build user profile from playlists and reviews

        Extract:
        - Top 3 favorite genres from playlists
        - Favorite artists from reviews (rating >= 4)
        - Counts for data sufficiency check
        """
        # Query top 3 genres from user's playlists
        genre_stmt = (
            select(Song.genre, func.count(Song.id).label("count"))
            .select_from(Playlist)
            .join(PlaylistSong, Playlist.id == PlaylistSong.playlist_id)
            .join(Song, PlaylistSong.song_id == Song.id)
            .where(
                Playlist.owner_user_id == user_id,
                Song.genre.isnot(None)
            )
            .group_by(Song.genre)
            .order_by(func.count(Song.id).desc())
            .limit(3)
        )
        genre_result = await self.db.execute(genre_stmt)
        favorite_genres = [row.genre for row in genre_result.all()]

        # Query favorite artists from reviews with rating >= 4
        artist_stmt = (
            select(Artist.id)
            .select_from(Review)
            .join(Song, Review.song_id == Song.id)
            .join(Album, Song.album_id == Album.id)
            .join(Artist, Album.artist_id == Artist.id)
            .where(
                Review.user_id == user_id,
                Review.rating >= 4
            )
            .distinct()
        )
        artist_result = await self.db.execute(artist_stmt)
        favorite_artists = [row.id for row in artist_result.all()]

        # Count playlist songs
        playlist_song_count_stmt = (
            select(func.count(PlaylistSong.id))
            .select_from(Playlist)
            .join(PlaylistSong, Playlist.id == PlaylistSong.playlist_id)
            .where(Playlist.owner_user_id == user_id)
        )
        playlist_song_count = await self.db.scalar(playlist_song_count_stmt) or 0

        # Count reviews
        review_count_stmt = (
            select(func.count(Review.id))
            .where(Review.user_id == user_id)
        )
        review_count = await self.db.scalar(review_count_stmt) or 0

        return UserProfile(
            favorite_genres=favorite_genres,
            favorite_artists=favorite_artists,
            playlist_song_count=int(playlist_song_count),
            review_count=int(review_count)
        )

    async def get_candidate_songs(self, user_id: int, limit: int = 100) -> List[dict]:
        """
        Get candidate songs for recommendations (excluding user's songs)

        Returns songs NOT in user's playlists or reviews
        """
        # Get user's song IDs from playlists
        playlist_songs_stmt = (
            select(PlaylistSong.song_id)
            .select_from(Playlist)
            .join(PlaylistSong, Playlist.id == PlaylistSong.playlist_id)
            .where(Playlist.owner_user_id == user_id)
        )

        # Get user's song IDs from reviews
        reviewed_songs_stmt = (
            select(Review.song_id)
            .where(Review.user_id == user_id)
        )

        # Union both sets
        user_song_ids_stmt = union(playlist_songs_stmt, reviewed_songs_stmt)
        user_song_ids_result = await self.db.execute(user_song_ids_stmt)
        user_song_ids = {row.song_id for row in user_song_ids_result.all()}

        # Query candidate songs (NOT in user's songs)
        stmt = (
            select(
                Song.id,
                Song.title,
                Song.genre,
                Song.average_rating,
                Song.review_count,
                Artist.name.label("artist_name"),
                Artist.id.label("artist_id"),
                Album.title.label("album_title")
            )
            .join(Album, Song.album_id == Album.id)
            .join(Artist, Album.artist_id == Artist.id)
            .where(
                Song.deleted_at.is_(None),
                ~Song.id.in_(user_song_ids) if user_song_ids else True
            )
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        return [
            {
                "id": row.id,
                "title": row.title,
                "genre": row.genre,
                "average_rating": row.average_rating,
                "review_count": row.review_count,
                "artist_name": row.artist_name,
                "artist_id": row.artist_id,
                "album_title": row.album_title
            }
            for row in rows
        ]

    async def get_popular_songs(self, limit: int = 20) -> List[dict]:
        """
        Get popular songs with high ratings and review counts

        Filters:
        - average_rating >= 4.0
        - review_count >= 10
        - Not soft-deleted
        """
        stmt = (
            select(
                Song.id,
                Song.title,
                Song.genre,
                Song.average_rating,
                Song.review_count,
                Artist.name.label("artist_name"),
                Artist.id.label("artist_id"),
                Album.title.label("album_title")
            )
            .join(Album, Song.album_id == Album.id)
            .join(Artist, Album.artist_id == Artist.id)
            .where(
                Song.deleted_at.is_(None),
                Song.average_rating >= 4.0,
                Song.review_count >= 10
            )
            .order_by(Song.review_count.desc())
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        return [
            {
                "id": row.id,
                "title": row.title,
                "genre": row.genre,
                "average_rating": row.average_rating,
                "review_count": row.review_count,
                "artist_name": row.artist_name,
                "artist_id": row.artist_id,
                "album_title": row.album_title
            }
            for row in rows
        ]

    async def get_songs_by_ids(self, song_ids: List[int]) -> List[dict]:
        """
        Get songs by IDs (for cache hits)
        """
        stmt = (
            select(
                Song.id,
                Song.title,
                Song.genre,
                Song.average_rating,
                Song.review_count,
                Artist.name.label("artist_name"),
                Artist.id.label("artist_id"),
                Album.title.label("album_title")
            )
            .join(Album, Song.album_id == Album.id)
            .join(Artist, Album.artist_id == Artist.id)
            .where(
                Song.id.in_(song_ids),
                Song.deleted_at.is_(None)
            )
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        return [
            {
                "id": row.id,
                "title": row.title,
                "genre": row.genre,
                "average_rating": row.average_rating,
                "review_count": row.review_count,
                "artist_name": row.artist_name,
                "artist_id": row.artist_id,
                "album_title": row.album_title
            }
            for row in rows
        ]
