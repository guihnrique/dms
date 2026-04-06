"""
Album Repository - Task 6.1, 6.2
Data access layer for Album entity with CRUD, pagination, and relationships
Requirements: 5.1-7.6, 12.1-12.6
"""
from typing import List, Tuple, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.album import Album
from app.models.artist import Artist
from app.models.song import Song


class AlbumRepository:
    """Repository for Album entity operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, title: str, artist_id: int, release_year: int, album_cover_url: Optional[str] = None) -> Album:
        """Create new album"""
        album = Album(
            title=title,
            artist_id=artist_id,
            release_year=release_year,
            album_cover_url=album_cover_url
        )
        self.db.add(album)
        await self.db.commit()
        await self.db.refresh(album)
        return album

    async def get_by_id(self, album_id: int) -> Optional[Album]:
        """Get album by ID with artist relationship"""
        result = await self.db.execute(
            select(Album)
            .options(selectinload(Album.artist))
            .where(Album.id == album_id)
        )
        return result.scalar_one_or_none()

    async def update(self, album_id: int, **kwargs) -> Optional[Album]:
        """Update album record"""
        album = await self.get_by_id(album_id)
        if not album:
            return None

        for key, value in kwargs.items():
            if hasattr(album, key):
                setattr(album, key, value)

        await self.db.commit()
        await self.db.refresh(album)
        return album

    async def list_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        artist_id: Optional[int] = None
    ) -> Tuple[List[Album], int]:
        """List albums with pagination, filtering, and sorting"""
        page_size = min(page_size, 100)
        offset = (page - 1) * page_size

        # Build query with optional artist filter
        query = select(Album).options(selectinload(Album.artist))
        if artist_id:
            query = query.where(Album.artist_id == artist_id)

        # Order by release_year DESC, title ASC (Requirement 6.2)
        query = query.order_by(Album.release_year.desc(), Album.title.asc())
        query = query.limit(page_size).offset(offset)

        result = await self.db.execute(query)
        items = result.scalars().all()

        # Get total count
        count_query = select(func.count()).select_from(Album)
        if artist_id:
            count_query = count_query.where(Album.artist_id == artist_id)
        total = await self.db.scalar(count_query)

        return list(items), total

    async def get_albums_with_song_stats(
        self,
        album_ids: List[int]
    ) -> List[dict]:
        """Get albums with songs_count and total_duration"""
        result = await self.db.execute(
            select(
                Album.id,
                Album.title,
                Album.artist_id,
                Album.release_year,
                Album.album_cover_url,
                Album.created_at,
                Album.updated_at,
                Artist.name.label("artist_name"),
                func.count(Song.id).label("songs_count"),
                func.coalesce(func.sum(Song.duration_seconds), 0).label("total_duration_seconds")
            )
            .outerjoin(Artist, Album.artist_id == Artist.id)
            .outerjoin(Song, Album.id == Song.album_id)
            .where(Album.id.in_(album_ids))
            .where(Song.deleted_at.is_(None))  # Exclude deleted songs
            .group_by(Album.id, Artist.name)
        )

        albums = []
        for row in result:
            albums.append({
                "id": row.id,
                "title": row.title,
                "artist_id": row.artist_id,
                "artist_name": row.artist_name,
                "release_year": row.release_year,
                "album_cover_url": row.album_cover_url,
                "songs_count": row.songs_count,
                "total_duration_seconds": row.total_duration_seconds,
                "created_at": row.created_at,
                "updated_at": row.updated_at
            })

        return albums
