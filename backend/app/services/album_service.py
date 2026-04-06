"""
Album Service - Task 7.1-7.3
Business logic layer for Album entity with artist validation
Requirements: 5.1-7.6
"""
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.album_repository import AlbumRepository
from app.repositories.artist_repository import ArtistRepository
from app.services.validation_service import ValidationService
from app.models.album import Album


class AlbumResponse:
    """Album response with artist and song stats"""
    def __init__(self, album: Album, artist_name: str = None, songs_count: int = 0, total_duration_seconds: int = 0):
        self.id = album.id
        self.title = album.title
        self.artist_id = album.artist_id
        self.artist_name = artist_name or (album.artist.name if album.artist else None)
        self.release_year = album.release_year
        self.album_cover_url = album.album_cover_url
        self.songs_count = songs_count
        self.total_duration_seconds = total_duration_seconds
        self.created_at = album.created_at
        self.updated_at = album.updated_at


class AlbumService:
    """Business logic for Album operations"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.album_repo = AlbumRepository(db)
        self.artist_repo = ArtistRepository(db)
        self.validation_service = ValidationService()

    async def create_album(
        self,
        title: str,
        artist_id: int,
        release_year: int,
        album_cover_url: Optional[str] = None
    ) -> AlbumResponse:
        """Create new album with validation"""
        # Sanitize title
        title = self.validation_service.sanitize_text(title)

        # Validate title length
        if len(title) > 200:
            raise ValueError("Album title must be at most 200 characters")

        # Validate artist exists
        artist = await self.artist_repo.get_by_id(artist_id)
        if not artist:
            raise ValueError("Artist not found")

        # Validate release year
        if not self.validation_service.validate_release_year(release_year):
            raise ValueError(f"Release year must be between 1900 and {self.validation_service.validate_release_year.__doc__}")

        # Validate album cover URL if provided
        if album_cover_url and not self.validation_service.validate_url(album_cover_url):
            raise ValueError("Invalid album cover URL")

        # Create album
        album = await self.album_repo.create(
            title=title,
            artist_id=artist_id,
            release_year=release_year,
            album_cover_url=album_cover_url
        )

        return AlbumResponse(album, artist_name=artist.name, songs_count=0, total_duration_seconds=0)

    async def get_album_by_id(self, album_id: int) -> Optional[AlbumResponse]:
        """Get album by ID with song stats"""
        album = await self.album_repo.get_by_id(album_id)
        if not album:
            return None

        # Get song stats
        albums_with_stats = await self.album_repo.get_albums_with_song_stats([album_id])

        if not albums_with_stats:
            return AlbumResponse(album, songs_count=0, total_duration_seconds=0)

        stats = albums_with_stats[0]
        return AlbumResponse(
            album,
            artist_name=stats["artist_name"],
            songs_count=stats["songs_count"],
            total_duration_seconds=stats["total_duration_seconds"]
        )

    async def list_albums(
        self,
        page: int = 1,
        page_size: int = 20,
        artist_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """List albums with pagination and filtering"""
        items, total = await self.album_repo.list_paginated(page=page, page_size=page_size, artist_id=artist_id)

        if items:
            album_ids = [album.id for album in items]
            albums_with_stats = await self.album_repo.get_albums_with_song_stats(album_ids)
            stats_map = {a["id"]: a for a in albums_with_stats}

            responses = [
                AlbumResponse(
                    album,
                    artist_name=stats_map.get(album.id, {}).get("artist_name"),
                    songs_count=stats_map.get(album.id, {}).get("songs_count", 0),
                    total_duration_seconds=stats_map.get(album.id, {}).get("total_duration_seconds", 0)
                )
                for album in items
            ]
        else:
            responses = []

        return {
            "items": responses,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    async def update_album(
        self,
        album_id: int,
        title: Optional[str] = None,
        release_year: Optional[int] = None,
        album_cover_url: Optional[str] = None
    ) -> Optional[AlbumResponse]:
        """Update album with validation"""
        update_data = {}

        if title is not None:
            title = self.validation_service.sanitize_text(title)
            if len(title) > 200:
                raise ValueError("Album title must be at most 200 characters")
            update_data["title"] = title

        if release_year is not None:
            if not self.validation_service.validate_release_year(release_year):
                raise ValueError("Invalid release year")
            update_data["release_year"] = release_year

        if album_cover_url is not None:
            if album_cover_url and not self.validation_service.validate_url(album_cover_url):
                raise ValueError("Invalid album cover URL")
            update_data["album_cover_url"] = album_cover_url

        album = await self.album_repo.update(album_id, **update_data)
        if not album:
            return None

        # Get updated stats
        albums_with_stats = await self.album_repo.get_albums_with_song_stats([album_id])
        stats = albums_with_stats[0] if albums_with_stats else {}

        return AlbumResponse(
            album,
            artist_name=stats.get("artist_name"),
            songs_count=stats.get("songs_count", 0),
            total_duration_seconds=stats.get("total_duration_seconds", 0)
        )
