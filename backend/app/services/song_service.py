"""
Song Service - Task 10.1-10.4
Business logic layer for Song entity with album validation and soft delete
Requirements: 9.1-11.7
"""
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.song_repository import SongRepository
from app.repositories.album_repository import AlbumRepository
from app.services.validation_service import ValidationService
from app.models.song import Song


class SongResponse:
    """Song response with album and artist details"""
    def __init__(
        self,
        song: Song,
        album_title: str = None,
        artist_id: int = None,
        artist_name: str = None
    ):
        self.id = song.id
        self.title = song.title
        self.album_id = song.album_id
        self.album_title = album_title or (song.album.title if song.album else None)
        self.artist_id = artist_id or (song.album.artist_id if song.album else None)
        self.artist_name = artist_name or (song.album.artist.name if song.album and song.album.artist else None)
        self.duration_seconds = song.duration_seconds
        self.genre = song.genre
        self.year = song.year
        self.cover_art_url = song.album.album_cover_url if song.album else None
        self.external_links = song.external_links
        self.deleted_at = song.deleted_at
        self.created_at = song.created_at
        self.updated_at = song.updated_at


class SongService:
    """Business logic for Song operations with soft delete"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.song_repo = SongRepository(db)
        self.album_repo = AlbumRepository(db)
        self.validation_service = ValidationService()

    async def create_song(
        self,
        title: str,
        album_id: int,
        duration_seconds: int,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        external_links: Optional[dict] = None
    ) -> SongResponse:
        """Create new song with validation"""
        # Sanitize title
        title = self.validation_service.sanitize_text(title)

        # Validate title length
        if len(title) > 200:
            raise ValueError("Song title must be at most 200 characters")

        # Validate album exists
        album = await self.album_repo.get_by_id(album_id)
        if not album:
            raise ValueError("Album not found")

        # Validate duration
        if not self.validation_service.validate_duration_seconds(duration_seconds):
            raise ValueError("Duration must be between 1 and 7200 seconds")

        # Validate year if provided
        if year is not None and not self.validation_service.validate_release_year(year):
            raise ValueError(f"Invalid release year")

        # Validate genre length if provided
        if genre is not None:
            genre = self.validation_service.sanitize_text(genre)
            if len(genre) > 50:
                raise ValueError("Genre must be at most 50 characters")

        # Create song
        song = await self.song_repo.create(
            title=title,
            album_id=album_id,
            duration_seconds=duration_seconds,
            genre=genre,
            year=year,
            external_links=external_links
        )

        return SongResponse(
            song,
            album_title=album.title,
            artist_id=album.artist_id,
            artist_name=album.artist.name if album.artist else None
        )

    async def get_song_by_id(self, song_id: int, include_deleted: bool = False) -> Optional[SongResponse]:
        """Get song by ID, excluding deleted by default"""
        song = await self.song_repo.get_by_id(song_id, include_deleted=include_deleted)
        if not song:
            return None

        return SongResponse(song)

    async def list_songs(
        self,
        page: int = 1,
        page_size: int = 20,
        album_id: Optional[int] = None,
        artist_id: Optional[int] = None,
        include_deleted: bool = False
    ) -> Dict[str, Any]:
        """List songs with pagination and filtering"""
        items, total = await self.song_repo.list_paginated(
            page=page,
            page_size=page_size,
            album_id=album_id,
            artist_id=artist_id,
            include_deleted=include_deleted
        )

        responses = [SongResponse(song) for song in items]

        return {
            "items": responses,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    async def update_song(
        self,
        song_id: int,
        title: Optional[str] = None,
        duration_seconds: Optional[int] = None,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        external_links: Optional[dict] = None
    ) -> Optional[SongResponse]:
        """Update song with validation"""
        update_data = {}

        if title is not None:
            title = self.validation_service.sanitize_text(title)
            if len(title) > 200:
                raise ValueError("Song title must be at most 200 characters")
            update_data["title"] = title

        if duration_seconds is not None:
            if not self.validation_service.validate_duration_seconds(duration_seconds):
                raise ValueError("Duration must be between 1 and 7200 seconds")
            update_data["duration_seconds"] = duration_seconds

        if genre is not None:
            genre = self.validation_service.sanitize_text(genre)
            if len(genre) > 50:
                raise ValueError("Genre must be at most 50 characters")
            update_data["genre"] = genre

        if year is not None:
            if not self.validation_service.validate_release_year(year):
                raise ValueError("Invalid release year")
            update_data["year"] = year

        if external_links is not None:
            update_data["external_links"] = external_links

        song = await self.song_repo.update(song_id, **update_data)
        if not song:
            return None

        return SongResponse(song)

    async def soft_delete_song(self, song_id: int) -> bool:
        """Soft delete song by setting deleted_at timestamp"""
        return await self.song_repo.soft_delete(song_id)

    async def restore_song(self, song_id: int) -> Optional[SongResponse]:
        """Restore soft-deleted song"""
        song = await self.song_repo.restore(song_id)
        if not song:
            return None

        return SongResponse(song)
