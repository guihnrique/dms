"""
Test PlaylistSongRepository for join table access - Task 3.2
Test-Driven Development (TDD): RED-GREEN phases

Requirements: 5, 6, 11, 12
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession


class TestPlaylistSongRepository:
    """Test PlaylistSong repository methods - Task 3.2"""

    async def _create_test_user(self, db_session):
        """Helper to create a test user"""
        from app.models.user import User
        from app.services.password_service import PasswordService
        from faker import Faker

        fake = Faker()
        password_service = PasswordService()
        user = User(
            email=fake.email(),
            password_hash=password_service.hash_password("TestPass123!"),
            role="user"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    @pytest.mark.asyncio
    async def test_add_song_assigns_next_position(self, db_session: AsyncSession, test_song):
        """
        RED phase - Test add_song assigns position max + 1
        Task 3.2: Implement add_song querying max position, creating with position = max + 1
        Requirement: 5 (Add Song to Playlist)
        """
        from app.repositories.playlist_repository import PlaylistRepository
        from app.repositories.playlist_song_repository import PlaylistSongRepository

        user = await self._create_test_user(db_session)
        playlist_repo = PlaylistRepository(db_session)
        song_repo = PlaylistSongRepository(db_session)

        # Create playlist
        playlist = await playlist_repo.create("Test Playlist", user.id, False)

        # Add first song - should get position 1
        ps1 = await song_repo.add_song(playlist.id, test_song.id)
        assert ps1.position == 1
        assert ps1.playlist_id == playlist.id
        assert ps1.song_id == test_song.id

        # Add same song again - should get position 2 (duplicates allowed)
        ps2 = await song_repo.add_song(playlist.id, test_song.id)
        assert ps2.position == 2

    @pytest.mark.asyncio
    async def test_add_song_allows_duplicates(self, db_session: AsyncSession, test_song):
        """
        RED phase - Test duplicate songs allowed via surrogate key
        Task 3.2: Allow duplicate songs by using surrogate key
        Requirement: 12 (Duplicate Song Handling)
        """
        from app.repositories.playlist_repository import PlaylistRepository
        from app.repositories.playlist_song_repository import PlaylistSongRepository

        user = await self._create_test_user(db_session)
        playlist_repo = PlaylistRepository(db_session)
        song_repo = PlaylistSongRepository(db_session)

        playlist = await playlist_repo.create("Test Playlist", user.id, False)

        # Add same song 3 times
        ps1 = await song_repo.add_song(playlist.id, test_song.id)
        ps2 = await song_repo.add_song(playlist.id, test_song.id)
        ps3 = await song_repo.add_song(playlist.id, test_song.id)

        # Verify all have different IDs
        assert ps1.id != ps2.id != ps3.id
        assert ps1.position == 1
        assert ps2.position == 2
        assert ps3.position == 3

    @pytest.mark.asyncio
    async def test_remove_song_by_playlist_song_id(self, db_session: AsyncSession, test_song):
        """
        RED phase - Test remove_song deletes specific entry
        Task 3.2: Implement remove_song deleting playlist_song entry
        Requirement: 6 (Remove Song from Playlist)
        """
        from app.repositories.playlist_repository import PlaylistRepository
        from app.repositories.playlist_song_repository import PlaylistSongRepository

        user = await self._create_test_user(db_session)
        playlist_repo = PlaylistRepository(db_session)
        song_repo = PlaylistSongRepository(db_session)

        playlist = await playlist_repo.create("Test Playlist", user.id, False)

        # Add 3 instances of same song
        ps1 = await song_repo.add_song(playlist.id, test_song.id)
        ps2 = await song_repo.add_song(playlist.id, test_song.id)
        ps3 = await song_repo.add_song(playlist.id, test_song.id)

        # Remove middle instance
        result = await song_repo.remove_song(ps2.id)
        assert result == True

        # Verify only specific instance removed
        songs = await song_repo.get_songs(playlist.id)
        assert len(songs) == 2

    @pytest.mark.asyncio
    async def test_remove_song_reorders_positions(self, db_session: AsyncSession, test_song):
        """
        RED phase - Test positions reordered after removal
        Task 3.2: Calling _reorder_positions to fill gaps
        Requirement: 6 (Remove Song from Playlist)
        """
        from app.repositories.playlist_repository import PlaylistRepository
        from app.repositories.playlist_song_repository import PlaylistSongRepository

        user = await self._create_test_user(db_session)
        playlist_repo = PlaylistRepository(db_session)
        song_repo = PlaylistSongRepository(db_session)

        playlist = await playlist_repo.create("Test Playlist", user.id, False)

        # Add 3 songs
        ps1 = await song_repo.add_song(playlist.id, test_song.id)
        ps2 = await song_repo.add_song(playlist.id, test_song.id)
        ps3 = await song_repo.add_song(playlist.id, test_song.id)

        # Remove middle song (position 2)
        await song_repo.remove_song(ps2.id)

        # Verify positions are sequential (1, 2) not (1, 3)
        songs = await song_repo.get_songs(playlist.id)
        positions = [s['position'] for s in songs]
        assert positions == [1, 2], "Positions should be reordered to fill gaps"

    @pytest.mark.asyncio
    async def test_get_songs_returns_full_details(self, db_session: AsyncSession, test_song):
        """
        RED phase - Test get_songs joins with songs, albums, artists
        Task 3.2: Implement get_songs joining tables, returning full details
        Requirement: 11 (Playlist Song Details)
        """
        from app.repositories.playlist_repository import PlaylistRepository
        from app.repositories.playlist_song_repository import PlaylistSongRepository

        user = await self._create_test_user(db_session)
        playlist_repo = PlaylistRepository(db_session)
        song_repo = PlaylistSongRepository(db_session)

        playlist = await playlist_repo.create("Test Playlist", user.id, False)

        # Add song
        await song_repo.add_song(playlist.id, test_song.id)

        # Get songs with full details
        songs = await song_repo.get_songs(playlist.id)

        assert len(songs) == 1
        song_detail = songs[0]
        assert 'playlist_song_id' in song_detail
        assert 'position' in song_detail
        assert 'song_id' in song_detail
        assert 'song_title' in song_detail
        assert 'artist_name' in song_detail
        assert 'album_title' in song_detail
        assert 'duration_seconds' in song_detail

    @pytest.mark.asyncio
    async def test_get_songs_excludes_soft_deleted(self, db_session: AsyncSession, test_song):
        """
        RED phase - Test soft-deleted songs excluded from results
        Task 3.2: Filter WHERE deleted_at IS NULL
        Requirement: 11 (Soft-Delete Filtering)
        """
        from app.repositories.playlist_repository import PlaylistRepository
        from app.repositories.playlist_song_repository import PlaylistSongRepository
        from app.models.song import Song
        from datetime import datetime

        user = await self._create_test_user(db_session)
        playlist_repo = PlaylistRepository(db_session)
        song_repo = PlaylistSongRepository(db_session)

        playlist = await playlist_repo.create("Test Playlist", user.id, False)

        # Add song
        await song_repo.add_song(playlist.id, test_song.id)

        # Soft-delete the song
        song_obj = await db_session.get(Song, test_song.id)
        song_obj.deleted_at = datetime.now()
        await db_session.commit()

        # Get songs - should be empty
        songs = await song_repo.get_songs(playlist.id)
        assert len(songs) == 0, "Soft-deleted songs should be excluded"

    @pytest.mark.asyncio
    async def test_get_songs_pagination(self, db_session: AsyncSession, test_song):
        """
        RED phase - Test get_songs with pagination
        Task 3.2: Implement pagination with page and page_size
        """
        from app.repositories.playlist_repository import PlaylistRepository
        from app.repositories.playlist_song_repository import PlaylistSongRepository

        user = await self._create_test_user(db_session)
        playlist_repo = PlaylistRepository(db_session)
        song_repo = PlaylistSongRepository(db_session)

        playlist = await playlist_repo.create("Test Playlist", user.id, False)

        # Add 5 songs
        for _ in range(5):
            await song_repo.add_song(playlist.id, test_song.id)

        # Get page 1 with page_size=2
        songs_p1 = await song_repo.get_songs(playlist.id, page=1, page_size=2)
        assert len(songs_p1) == 2
        assert songs_p1[0]['position'] == 1
        assert songs_p1[1]['position'] == 2

        # Get page 2 with page_size=2
        songs_p2 = await song_repo.get_songs(playlist.id, page=2, page_size=2)
        assert len(songs_p2) == 2
        assert songs_p2[0]['position'] == 3
        assert songs_p2[1]['position'] == 4

    @pytest.mark.asyncio
    async def test_get_songs_ordered_by_position(self, db_session: AsyncSession, test_song):
        """
        RED phase - Test songs ordered by position ASC
        Task 3.2: Order by position ASC
        """
        from app.repositories.playlist_repository import PlaylistRepository
        from app.repositories.playlist_song_repository import PlaylistSongRepository

        user = await self._create_test_user(db_session)
        playlist_repo = PlaylistRepository(db_session)
        song_repo = PlaylistSongRepository(db_session)

        playlist = await playlist_repo.create("Test Playlist", user.id, False)

        # Add songs
        for _ in range(3):
            await song_repo.add_song(playlist.id, test_song.id)

        # Get songs
        songs = await song_repo.get_songs(playlist.id)

        # Verify ordered by position
        positions = [s['position'] for s in songs]
        assert positions == [1, 2, 3], "Songs should be ordered by position ASC"

    @pytest.mark.asyncio
    async def test_get_max_position(self, db_session: AsyncSession, test_song):
        """
        RED phase - Test get_max_position returns max position
        Task 3.2: Implement get_max_position returning max(position)
        """
        from app.repositories.playlist_repository import PlaylistRepository
        from app.repositories.playlist_song_repository import PlaylistSongRepository

        user = await self._create_test_user(db_session)
        playlist_repo = PlaylistRepository(db_session)
        song_repo = PlaylistSongRepository(db_session)

        playlist = await playlist_repo.create("Test Playlist", user.id, False)

        # Empty playlist - max should be 0
        max_pos = await song_repo.get_max_position(playlist.id)
        assert max_pos == 0

        # Add 3 songs
        await song_repo.add_song(playlist.id, test_song.id)
        await song_repo.add_song(playlist.id, test_song.id)
        await song_repo.add_song(playlist.id, test_song.id)

        # Max should be 3
        max_pos = await song_repo.get_max_position(playlist.id)
        assert max_pos == 3
