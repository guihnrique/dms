"""
Song Repository - Task 9.1-9.3
Data access layer for Song entity with soft delete support
Requirements: 8.1-11.7
"""
from typing import List, Tuple, Optional
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.song import Song
from app.models.album import Album
from app.models.artist import Artist


class SongRepository:
    """Repository for Song entity operations with soft delete"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        title: str,
        album_id: int,
        duration_seconds: int,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        external_links: Optional[dict] = None
    ) -> Song:
        """Create new song"""
        song = Song(
            title=title,
            album_id=album_id,
            duration_seconds=duration_seconds,
            genre=genre,
            year=year,
            external_links=external_links
        )
        self.db.add(song)
        await self.db.commit()
        await self.db.refresh(song)
        return song

    async def get_by_id(self, song_id: int, include_deleted: bool = False) -> Optional[Song]:
        """Get song by ID, excluding deleted by default"""
        query = select(Song).options(
            selectinload(Song.album).selectinload(Album.artist)
        ).where(Song.id == song_id)

        if not include_deleted:
            query = query.where(Song.deleted_at.is_(None))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update(self, song_id: int, **kwargs) -> Optional[Song]:
        """Update song record"""
        song = await self.get_by_id(song_id, include_deleted=False)
        if not song:
            return None

        for key, value in kwargs.items():
            if hasattr(song, key):
                setattr(song, key, value)

        await self.db.commit()
        await self.db.refresh(song)
        return song

    async def soft_delete(self, song_id: int) -> bool:
        """Soft delete song by setting deleted_at timestamp"""
        song = await self.get_by_id(song_id, include_deleted=False)
        if not song:
            return False

        song.deleted_at = datetime.utcnow()
        await self.db.commit()
        return True

    async def restore(self, song_id: int) -> Optional[Song]:
        """Restore soft-deleted song"""
        song = await self.get_by_id(song_id, include_deleted=True)
        if not song or not song.deleted_at:
            return None

        song.deleted_at = None
        await self.db.commit()
        await self.db.refresh(song)
        return song

    async def list_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        album_id: Optional[int] = None,
        include_deleted: bool = False
    ) -> Tuple[List[Song], int]:
        """List songs with pagination, excluding deleted by default"""
        page_size = min(page_size, 100)
        offset = (page - 1) * page_size

        query = select(Song).options(
            selectinload(Song.album).selectinload(Album.artist)
        )

        if album_id:
            query = query.where(Song.album_id == album_id)

        if not include_deleted:
            query = query.where(Song.deleted_at.is_(None))

        query = query.order_by(Song.title).limit(page_size).offset(offset)

        result = await self.db.execute(query)
        items = result.scalars().all()

        # Get total count
        count_query = select(func.count()).select_from(Song)
        if album_id:
            count_query = count_query.where(Song.album_id == album_id)
        if not include_deleted:
            count_query = count_query.where(Song.deleted_at.is_(None))

        total = await self.db.scalar(count_query)

        return list(items), total

    async def update_average_rating(
        self,
        song_id: int,
        average_rating: Optional[float],
        review_count: int
    ) -> None:
        """
        Update song's denormalized rating data
        Task 3.3: Extend SongRepository for rating updates
        Requirements: 6
        """
        song = await self.get_by_id(song_id)
        if song:
            song.average_rating = average_rating
            song.review_count = review_count
            await self.db.commit()
