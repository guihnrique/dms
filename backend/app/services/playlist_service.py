"""
PlaylistService for business logic - Task 4.1, 4.2, 4.3, 4.4
Requirements: 1, 2, 3, 4, 5, 6, 7, 8, 9
"""
import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.repositories.playlist_repository import PlaylistRepository
from app.repositories.playlist_song_repository import PlaylistSongRepository
from app.repositories.song_repository import SongRepository
from app.schemas.playlist import PlaylistResponse

logger = logging.getLogger(__name__)


class PlaylistService:
    """
    Service for playlist business logic

    Handles:
    - CRUD operations with validation
    - Privacy enforcement (private → owner only)
    - Song management (add, remove, reorder)
    - Metadata calculation (songs_count, total_duration)
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.playlist_repo = PlaylistRepository(db)
        self.playlist_song_repo = PlaylistSongRepository(db)
        self.song_repo = SongRepository(db)

    async def create_playlist(
        self,
        title: str,
        owner_user_id: int,
        is_public: bool = False
    ) -> PlaylistResponse:
        """
        Create new playlist with validation

        Args:
            title: Playlist name (1-200 chars)
            owner_user_id: Owner user ID
            is_public: Privacy setting (default: False)

        Returns:
            PlaylistResponse with metadata

        Raises:
            ValueError: If title validation fails

        Requirements:
        - 1: Playlist Creation
        - 8: Default privacy is private
        """
        # Validate title length
        if not title or len(title.strip()) < 1:
            raise ValueError("Title must be at least 1 character")
        if len(title) > 200:
            raise ValueError("Title must be at most 200 characters")

        # Create playlist
        playlist = await self.playlist_repo.create(
            title=title.strip(),
            owner_user_id=owner_user_id,
            is_public=is_public
        )

        # Return with metadata
        return PlaylistResponse(
            id=playlist.id,
            title=playlist.title,
            owner_user_id=playlist.owner_user_id,
            is_public=playlist.is_public,
            songs_count=0,
            total_duration_seconds=0,
            created_at=playlist.created_at,
            updated_at=playlist.updated_at
        )

    async def get_playlist_by_id(
        self,
        playlist_id: int,
        current_user_id: Optional[int] = None
    ) -> PlaylistResponse:
        """
        Get playlist by ID with privacy enforcement

        Args:
            playlist_id: Playlist ID
            current_user_id: Current user ID (None for guest)

        Returns:
            PlaylistResponse with metadata

        Raises:
            HTTPException: 404 if not found, 403 if private and not owner

        Requirements:
        - 2: Playlist Retrieval
        - 8: Privacy enforcement (private → owner only)
        """
        # Get playlist
        playlist = await self.playlist_repo.get_by_id(playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        # Enforce privacy
        if not playlist.is_public and playlist.owner_user_id != current_user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have access to this private playlist"
            )

        # Calculate metadata
        songs = await self.playlist_song_repo.get_songs(playlist_id, page=1, page_size=10000)
        songs_count = len(songs)
        total_duration = sum(s['duration_seconds'] for s in songs)

        return PlaylistResponse(
            id=playlist.id,
            title=playlist.title,
            owner_user_id=playlist.owner_user_id,
            is_public=playlist.is_public,
            songs_count=songs_count,
            total_duration_seconds=total_duration,
            created_at=playlist.created_at,
            updated_at=playlist.updated_at
        )

    async def get_user_playlists(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        Get user's playlists with pagination

        Args:
            user_id: User ID
            page: Page number (1-indexed)
            page_size: Items per page

        Returns:
            Dict with items, total, page, page_size, total_pages

        Requirements:
        - 2: Playlist Retrieval with pagination
        """
        playlists, total = await self.playlist_repo.get_by_owner(
            user_id, page=page, page_size=page_size
        )

        # Convert to response models with metadata
        items = []
        for playlist in playlists:
            songs = await self.playlist_song_repo.get_songs(playlist.id, page=1, page_size=10000)
            items.append(PlaylistResponse(
                id=playlist.id,
                title=playlist.title,
                owner_user_id=playlist.owner_user_id,
                is_public=playlist.is_public,
                songs_count=len(songs),
                total_duration_seconds=sum(s['duration_seconds'] for s in songs),
                created_at=playlist.created_at,
                updated_at=playlist.updated_at
            ))

        total_pages = (total + page_size - 1) // page_size

        return {
            'items': items,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages
        }

    async def get_public_playlists(
        self,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        Get public playlists with pagination

        Args:
            page: Page number (1-indexed)
            page_size: Items per page

        Returns:
            Dict with items, total, page, page_size, total_pages

        Requirements:
        - 2: Public Playlist Retrieval
        - 8: Only public playlists
        """
        playlists, total = await self.playlist_repo.get_public(
            page=page, page_size=page_size
        )

        # Convert to response models with metadata
        items = []
        for playlist in playlists:
            songs = await self.playlist_song_repo.get_songs(playlist.id, page=1, page_size=10000)
            items.append(PlaylistResponse(
                id=playlist.id,
                title=playlist.title,
                owner_user_id=playlist.owner_user_id,
                is_public=playlist.is_public,
                songs_count=len(songs),
                total_duration_seconds=sum(s['duration_seconds'] for s in songs),
                created_at=playlist.created_at,
                updated_at=playlist.updated_at
            ))

        total_pages = (total + page_size - 1) // page_size

        return {
            'items': items,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages
        }

    async def update_playlist(
        self,
        playlist_id: int,
        title: Optional[str] = None,
        is_public: Optional[bool] = None
    ) -> PlaylistResponse:
        """
        Update playlist fields

        Args:
            playlist_id: Playlist ID
            title: New title (optional, validated 1-200 chars)
            is_public: New privacy setting (optional)

        Returns:
            Updated PlaylistResponse

        Raises:
            ValueError: If title validation fails

        Requirements:
        - 3: Playlist Update
        - 8: Privacy toggle
        """
        # Validate title if provided
        if title is not None:
            title = title.strip()
            if len(title) < 1:
                raise ValueError("Title must be at least 1 character")
            if len(title) > 200:
                raise ValueError("Title must be at most 200 characters")

        # Update
        updated = await self.playlist_repo.update(
            playlist_id,
            title=title,
            is_public=is_public
        )

        # Calculate metadata
        songs = await self.playlist_song_repo.get_songs(playlist_id, page=1, page_size=10000)

        return PlaylistResponse(
            id=updated.id,
            title=updated.title,
            owner_user_id=updated.owner_user_id,
            is_public=updated.is_public,
            songs_count=len(songs),
            total_duration_seconds=sum(s['duration_seconds'] for s in songs),
            created_at=updated.created_at,
            updated_at=updated.updated_at
        )

    async def delete_playlist(self, playlist_id: int) -> bool:
        """
        Delete playlist (hard delete, CASCADE removes playlist_songs)

        Args:
            playlist_id: Playlist ID

        Returns:
            True if deleted

        Requirements:
        - 4: Playlist Deletion with CASCADE
        """
        return await self.playlist_repo.delete(playlist_id)

    async def add_song_to_playlist(
        self,
        playlist_id: int,
        song_id: int
    ) -> PlaylistResponse:
        """
        Add song to playlist with validation

        Args:
            playlist_id: Playlist ID
            song_id: Song ID to add

        Returns:
            Updated PlaylistResponse

        Raises:
            HTTPException: 400 if song not found

        Requirements:
        - 5: Add Song to Playlist
        - 9: Warning at 1000 songs
        """
        # Validate song exists in catalog
        song = await self.song_repo.get_by_id(song_id)
        if not song:
            raise HTTPException(status_code=400, detail="Song not found in catalog")

        # Check current song count
        songs = await self.playlist_song_repo.get_songs(playlist_id, page=1, page_size=10000)
        if len(songs) >= 1000:
            logger.warning(
                f"Playlist {playlist_id} has {len(songs)} songs, "
                "exceeding recommended limit of 1000"
            )

        # Add song
        await self.playlist_song_repo.add_song(playlist_id, song_id)

        # Return updated playlist (without privacy check - internal call)
        playlist = await self.playlist_repo.get_by_id(playlist_id)
        songs = await self.playlist_song_repo.get_songs(playlist_id, page=1, page_size=10000)

        return PlaylistResponse(
            id=playlist.id,
            title=playlist.title,
            owner_user_id=playlist.owner_user_id,
            is_public=playlist.is_public,
            songs_count=len(songs),
            total_duration_seconds=sum(s['duration_seconds'] for s in songs),
            created_at=playlist.created_at,
            updated_at=playlist.updated_at
        )

    async def remove_song_from_playlist(
        self,
        playlist_id: int,
        playlist_song_id: int
    ) -> PlaylistResponse:
        """
        Remove song from playlist (specific instance)

        Args:
            playlist_id: Playlist ID
            playlist_song_id: PlaylistSong ID (specific instance)

        Returns:
            Updated PlaylistResponse

        Requirements:
        - 6: Remove Song from Playlist
        """
        # Remove song
        await self.playlist_song_repo.remove_song(playlist_song_id)

        # Return updated playlist (without privacy check - internal call)
        playlist = await self.playlist_repo.get_by_id(playlist_id)
        songs = await self.playlist_song_repo.get_songs(playlist_id, page=1, page_size=10000)

        return PlaylistResponse(
            id=playlist.id,
            title=playlist.title,
            owner_user_id=playlist.owner_user_id,
            is_public=playlist.is_public,
            songs_count=len(songs),
            total_duration_seconds=sum(s['duration_seconds'] for s in songs),
            created_at=playlist.created_at,
            updated_at=playlist.updated_at
        )

    async def reorder_song(
        self,
        playlist_id: int,
        playlist_song_id: int,
        new_position: int
    ) -> PlaylistResponse:
        """
        Reorder song to new position

        Args:
            playlist_id: Playlist ID
            playlist_song_id: PlaylistSong ID to move
            new_position: New position (1-indexed)

        Returns:
            Updated PlaylistResponse

        Raises:
            HTTPException: 400 if new_position out of bounds

        Requirements:
        - 7: Reorder Songs
        """
        try:
            # Reorder
            await self.playlist_song_repo.reorder_song(
                playlist_id,
                playlist_song_id,
                new_position
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Return updated playlist (without privacy check - internal call)
        playlist = await self.playlist_repo.get_by_id(playlist_id)
        songs = await self.playlist_song_repo.get_songs(playlist_id, page=1, page_size=10000)

        return PlaylistResponse(
            id=playlist.id,
            title=playlist.title,
            owner_user_id=playlist.owner_user_id,
            is_public=playlist.is_public,
            songs_count=len(songs),
            total_duration_seconds=sum(s['duration_seconds'] for s in songs),
            created_at=playlist.created_at,
            updated_at=playlist.updated_at
        )
