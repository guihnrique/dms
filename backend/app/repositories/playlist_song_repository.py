"""
PlaylistSongRepository for join table access - Task 3.2
Requirements: 5, 6, 11, 12
"""
from typing import List, Dict, Any
from sqlalchemy import select, func, delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.playlist import PlaylistSong
from app.models.song import Song
from app.models.album import Album
from app.models.artist import Artist


class PlaylistSongRepository:
    """
    Repository for PlaylistSong join table operations

    Implements song management within playlists with:
    - Position assignment (auto-increment)
    - Duplicate song support (surrogate key)
    - Position reordering after removal
    - Soft-delete filtering
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_song(self, playlist_id: int, song_id: int) -> PlaylistSong:
        """
        Add song to playlist with next available position

        Args:
            playlist_id: Playlist ID
            song_id: Song ID to add

        Returns:
            Created PlaylistSong instance with position = max + 1

        Requirements:
        - 5: Add Song to Playlist
        - 12: Allow duplicate songs
        """
        # Get max position
        max_position = await self.get_max_position(playlist_id)

        # Create new playlist_song with next position
        playlist_song = PlaylistSong(
            playlist_id=playlist_id,
            song_id=song_id,
            position=max_position + 1
        )

        self.db.add(playlist_song)
        await self.db.commit()
        await self.db.refresh(playlist_song)

        return playlist_song

    async def remove_song(self, playlist_song_id: int) -> bool:
        """
        Remove specific playlist_song entry and reorder positions

        Args:
            playlist_song_id: PlaylistSong ID (specific instance)

        Returns:
            True if deleted, False if not found

        Requirements:
        - 6: Remove Song from Playlist (specific instance)
        """
        # Get the playlist_song to find playlist_id
        stmt = select(PlaylistSong).where(PlaylistSong.id == playlist_song_id)
        result = await self.db.execute(stmt)
        playlist_song = result.scalar_one_or_none()

        if not playlist_song:
            return False

        playlist_id = playlist_song.playlist_id

        # Delete the entry
        delete_stmt = sql_delete(PlaylistSong).where(PlaylistSong.id == playlist_song_id)
        await self.db.execute(delete_stmt)
        await self.db.commit()

        # Reorder positions to fill gaps
        await self._reorder_positions(playlist_id)

        return True

    async def get_songs(
        self,
        playlist_id: int,
        page: int = 1,
        page_size: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get songs in playlist with full details and pagination

        Args:
            playlist_id: Playlist ID
            page: Page number (1-indexed)
            page_size: Items per page (default: 50)

        Returns:
            List of dicts with: playlist_song_id, position, song_id,
            song_title, artist_name, album_title, duration_seconds

        Requirements:
        - 11: Playlist Song Details with soft-delete filtering
        """
        offset = (page - 1) * page_size

        # Join with songs, albums, artists and filter soft-deleted
        stmt = (
            select(
                PlaylistSong.id.label('playlist_song_id'),
                PlaylistSong.position,
                Song.id.label('song_id'),
                Song.title.label('song_title'),
                Artist.name.label('artist_name'),
                Album.title.label('album_title'),
                Song.duration_seconds
            )
            .join(Song, PlaylistSong.song_id == Song.id)
            .join(Album, Song.album_id == Album.id)
            .join(Artist, Album.artist_id == Artist.id)
            .where(PlaylistSong.playlist_id == playlist_id)
            .where(Song.deleted_at.is_(None))  # Exclude soft-deleted songs
            .order_by(PlaylistSong.position.asc())
            .limit(page_size)
            .offset(offset)
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        # Convert to list of dicts
        songs = []
        for row in rows:
            songs.append({
                'playlist_song_id': row.playlist_song_id,
                'position': row.position,
                'song_id': row.song_id,
                'song_title': row.song_title,
                'artist_name': row.artist_name,
                'album_title': row.album_title,
                'duration_seconds': row.duration_seconds
            })

        return songs

    async def get_max_position(self, playlist_id: int) -> int:
        """
        Get maximum position in playlist

        Args:
            playlist_id: Playlist ID

        Returns:
            Maximum position (0 if empty)
        """
        stmt = select(func.max(PlaylistSong.position)).where(
            PlaylistSong.playlist_id == playlist_id
        )
        result = await self.db.execute(stmt)
        max_position = result.scalar()

        return max_position or 0

    async def reorder_song(
        self,
        playlist_id: int,
        playlist_song_id: int,
        new_position: int
    ) -> None:
        """
        Reorder song to new position with transaction and row-level locking

        Uses SELECT FOR UPDATE to prevent race conditions during concurrent reorders

        Args:
            playlist_id: Playlist ID
            playlist_song_id: PlaylistSong ID to move
            new_position: New position (1-indexed, must be within bounds)

        Raises:
            ValueError: If new_position out of bounds or playlist_song not found

        Requirements:
        - 7: Reorder Songs with transaction isolation
        """
        # Begin transaction with row-level locking (SELECT FOR UPDATE)
        # Get all playlist_songs in order with lock
        stmt = (
            select(PlaylistSong)
            .where(PlaylistSong.playlist_id == playlist_id)
            .order_by(PlaylistSong.position.asc())
            .with_for_update()  # Row-level lock
        )
        result = await self.db.execute(stmt)
        playlist_songs = list(result.scalars().all())

        if not playlist_songs:
            raise ValueError("Playlist is empty")

        # Find target song
        target_song = None
        old_position = None
        for idx, ps in enumerate(playlist_songs):
            if ps.id == playlist_song_id:
                target_song = ps
                old_position = idx + 1  # Convert to 1-indexed
                break

        if not target_song:
            raise ValueError(f"PlaylistSong {playlist_song_id} not found in playlist")

        # Validate new_position bounds
        if new_position < 1 or new_position > len(playlist_songs):
            raise ValueError(
                f"Position {new_position} out of bounds (1-{len(playlist_songs)})"
            )

        # No-op if same position
        if new_position == old_position:
            return

        # Remove target from list
        playlist_songs.pop(old_position - 1)

        # Insert at new position (convert to 0-indexed)
        playlist_songs.insert(new_position - 1, target_song)

        # Renumber all positions sequentially
        for idx, ps in enumerate(playlist_songs, start=1):
            ps.position = idx

        # Commit transaction
        await self.db.commit()

    async def _reorder_positions(self, playlist_id: int) -> None:
        """
        Internal method to reorder positions sequentially after removal

        Fills gaps in position sequence (e.g., 1, 3, 5 becomes 1, 2, 3)

        Args:
            playlist_id: Playlist ID

        Requirements:
        - 6: Fill gaps after song removal
        """
        # Get all playlist_songs ordered by position
        stmt = (
            select(PlaylistSong)
            .where(PlaylistSong.playlist_id == playlist_id)
            .order_by(PlaylistSong.position.asc())
        )
        result = await self.db.execute(stmt)
        playlist_songs = result.scalars().all()

        # Renumber positions sequentially
        for idx, ps in enumerate(playlist_songs, start=1):
            if ps.position != idx:
                ps.position = idx

        await self.db.commit()
