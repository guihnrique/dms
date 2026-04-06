"""
PlaylistRepository for data access - Task 3.1
Requirements: 1, 2, 3, 4, 8
"""
from typing import Optional, Tuple, List
from sqlalchemy import select, func, update as sql_update, delete as sql_delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.playlist import Playlist


class PlaylistRepository:
    """
    Repository for Playlist data access operations

    Implements CRUD operations with pagination support
    Requirements:
    - 1: Playlist Creation
    - 2: Playlist Retrieval (with pagination)
    - 3: Playlist Update
    - 4: Playlist Deletion
    - 8: Privacy Control
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        title: str,
        owner_user_id: int,
        is_public: bool = False
    ) -> Playlist:
        """
        Create a new playlist

        Args:
            title: Playlist name (1-200 chars)
            owner_user_id: ID of the owner user
            is_public: Privacy setting (default: False)

        Returns:
            Created Playlist instance with timestamps
        """
        playlist = Playlist(
            title=title,
            owner_user_id=owner_user_id,
            is_public=is_public
        )

        self.db.add(playlist)
        await self.db.commit()
        await self.db.refresh(playlist)

        return playlist

    async def get_by_id(self, playlist_id: int) -> Optional[Playlist]:
        """
        Get playlist by ID with eager loading of songs

        Args:
            playlist_id: Playlist ID

        Returns:
            Playlist instance or None if not found
        """
        stmt = (
            select(Playlist)
            .options(selectinload(Playlist.playlist_songs))
            .where(Playlist.id == playlist_id)
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_owner(
        self,
        owner_user_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Playlist], int]:
        """
        Get playlists by owner with pagination

        Args:
            owner_user_id: Owner user ID
            page: Page number (1-indexed)
            page_size: Items per page (default: 20)

        Returns:
            Tuple of (playlists list, total count)
        """
        # Count total
        count_stmt = (
            select(func.count())
            .select_from(Playlist)
            .where(Playlist.owner_user_id == owner_user_id)
        )
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0

        # Get paginated results
        offset = (page - 1) * page_size
        stmt = (
            select(Playlist)
            .where(Playlist.owner_user_id == owner_user_id)
            .order_by(Playlist.created_at.desc())
            .limit(page_size)
            .offset(offset)
        )

        result = await self.db.execute(stmt)
        playlists = list(result.scalars().all())

        return playlists, total

    async def get_public(
        self,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Playlist], int]:
        """
        Get public playlists with pagination

        Args:
            page: Page number (1-indexed)
            page_size: Items per page (default: 20)

        Returns:
            Tuple of (playlists list, total count)
        """
        # Count total public playlists
        count_stmt = (
            select(func.count())
            .select_from(Playlist)
            .where(Playlist.is_public == True)
        )
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0

        # Get paginated results
        offset = (page - 1) * page_size
        stmt = (
            select(Playlist)
            .where(Playlist.is_public == True)
            .order_by(Playlist.created_at.desc())
            .limit(page_size)
            .offset(offset)
        )

        result = await self.db.execute(stmt)
        playlists = list(result.scalars().all())

        return playlists, total

    async def update(
        self,
        playlist_id: int,
        title: Optional[str] = None,
        is_public: Optional[bool] = None
    ) -> Optional[Playlist]:
        """
        Update playlist fields

        Args:
            playlist_id: Playlist ID
            title: New title (optional)
            is_public: New privacy setting (optional)

        Returns:
            Updated Playlist instance or None if not found
        """
        # Build update dict
        update_data = {}
        if title is not None:
            update_data['title'] = title
        if is_public is not None:
            update_data['is_public'] = is_public

        if not update_data:
            # No changes, just return existing playlist
            return await self.get_by_id(playlist_id)

        # Update with updated_at timestamp
        stmt = (
            sql_update(Playlist)
            .where(Playlist.id == playlist_id)
            .values(**update_data)
        )

        await self.db.execute(stmt)
        await self.db.commit()

        # Return updated playlist
        return await self.get_by_id(playlist_id)

    async def delete(self, playlist_id: int) -> bool:
        """
        Delete playlist (hard delete, CASCADE removes playlist_songs)

        Args:
            playlist_id: Playlist ID

        Returns:
            True if deleted, False if not found
        """
        stmt = sql_delete(Playlist).where(Playlist.id == playlist_id)

        result = await self.db.execute(stmt)
        await self.db.commit()

        return result.rowcount > 0
