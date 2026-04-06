"""
Test PlaylistSongRepository reordering logic - Task 3.3
Test-Driven Development (TDD): RED-GREEN phases

Requirements: 6, 7
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession


class TestPlaylistSongReordering:
    """Test song reordering with transactions - Task 3.3"""

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
    async def test_reorder_song_moves_to_new_position(self, db_session: AsyncSession, test_song):
        """
        RED phase - Test reorder_song moves song to new position
        Task 3.3: Implement reorder_song with transaction and locking
        Requirement: 7 (Reorder Songs)
        """
        from app.repositories.playlist_repository import PlaylistRepository
        from app.repositories.playlist_song_repository import PlaylistSongRepository

        user = await self._create_test_user(db_session)
        playlist_repo = PlaylistRepository(db_session)
        song_repo = PlaylistSongRepository(db_session)

        playlist = await playlist_repo.create("Test Playlist", user.id, False)

        # Add 5 songs
        ps1 = await song_repo.add_song(playlist.id, test_song.id)
        ps2 = await song_repo.add_song(playlist.id, test_song.id)
        ps3 = await song_repo.add_song(playlist.id, test_song.id)
        ps4 = await song_repo.add_song(playlist.id, test_song.id)
        ps5 = await song_repo.add_song(playlist.id, test_song.id)

        # Move position 5 to position 2
        await song_repo.reorder_song(playlist.id, ps5.id, 2)

        # Verify new order: [1, 5, 2, 3, 4]
        songs = await song_repo.get_songs(playlist.id)
        song_ids = [s['playlist_song_id'] for s in songs]
        assert song_ids == [ps1.id, ps5.id, ps2.id, ps3.id, ps4.id]

    @pytest.mark.asyncio
    async def test_reorder_song_positions_sequential(self, db_session: AsyncSession, test_song):
        """
        RED phase - Test positions remain sequential after reorder
        Task 3.3: Verify positions are 1, 2, 3, ... after reorder
        Requirement: 7 (Reorder Songs)
        """
        from app.repositories.playlist_repository import PlaylistRepository
        from app.repositories.playlist_song_repository import PlaylistSongRepository

        user = await self._create_test_user(db_session)
        playlist_repo = PlaylistRepository(db_session)
        song_repo = PlaylistSongRepository(db_session)

        playlist = await playlist_repo.create("Test Playlist", user.id, False)

        # Add 4 songs
        ps1 = await song_repo.add_song(playlist.id, test_song.id)
        ps2 = await song_repo.add_song(playlist.id, test_song.id)
        ps3 = await song_repo.add_song(playlist.id, test_song.id)
        ps4 = await song_repo.add_song(playlist.id, test_song.id)

        # Move position 1 to position 4
        await song_repo.reorder_song(playlist.id, ps1.id, 4)

        # Verify positions are sequential
        songs = await song_repo.get_songs(playlist.id)
        positions = [s['position'] for s in songs]
        assert positions == [1, 2, 3, 4], "Positions should be sequential"

    @pytest.mark.asyncio
    async def test_reorder_song_same_position_is_noop(self, db_session: AsyncSession, test_song):
        """
        RED phase - Test reordering to same position is no-op
        Task 3.3: Handle edge case new_position == old_position
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

        # Reorder to same position (2 -> 2)
        await song_repo.reorder_song(playlist.id, ps2.id, 2)

        # Verify order unchanged
        songs = await song_repo.get_songs(playlist.id)
        song_ids = [s['playlist_song_id'] for s in songs]
        assert song_ids == [ps1.id, ps2.id, ps3.id]

    @pytest.mark.asyncio
    async def test_reorder_song_invalid_position_raises_error(self, db_session: AsyncSession, test_song):
        """
        RED phase - Test invalid position raises ValueError
        Task 3.3: Handle edge case new_position out of bounds
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

        # Try to move to position 0 (invalid)
        with pytest.raises(ValueError) as exc_info:
            await song_repo.reorder_song(playlist.id, ps2.id, 0)
        assert "out of bounds" in str(exc_info.value).lower()

        # Try to move to position 5 (out of range)
        with pytest.raises(ValueError) as exc_info:
            await song_repo.reorder_song(playlist.id, ps2.id, 5)
        assert "out of bounds" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_reorder_song_move_forward(self, db_session: AsyncSession, test_song):
        """
        RED phase - Test moving song forward in playlist
        Task 3.3: Test moving from lower to higher position
        """
        from app.repositories.playlist_repository import PlaylistRepository
        from app.repositories.playlist_song_repository import PlaylistSongRepository

        user = await self._create_test_user(db_session)
        playlist_repo = PlaylistRepository(db_session)
        song_repo = PlaylistSongRepository(db_session)

        playlist = await playlist_repo.create("Test Playlist", user.id, False)

        # Add 4 songs
        ps1 = await song_repo.add_song(playlist.id, test_song.id)
        ps2 = await song_repo.add_song(playlist.id, test_song.id)
        ps3 = await song_repo.add_song(playlist.id, test_song.id)
        ps4 = await song_repo.add_song(playlist.id, test_song.id)

        # Move position 2 to position 4
        await song_repo.reorder_song(playlist.id, ps2.id, 4)

        # Verify new order: [1, 3, 4, 2]
        songs = await song_repo.get_songs(playlist.id)
        song_ids = [s['playlist_song_id'] for s in songs]
        assert song_ids == [ps1.id, ps3.id, ps4.id, ps2.id]

    @pytest.mark.asyncio
    async def test_reorder_song_move_backward(self, db_session: AsyncSession, test_song):
        """
        RED phase - Test moving song backward in playlist
        Task 3.3: Test moving from higher to lower position
        """
        from app.repositories.playlist_repository import PlaylistRepository
        from app.repositories.playlist_song_repository import PlaylistSongRepository

        user = await self._create_test_user(db_session)
        playlist_repo = PlaylistRepository(db_session)
        song_repo = PlaylistSongRepository(db_session)

        playlist = await playlist_repo.create("Test Playlist", user.id, False)

        # Add 4 songs
        ps1 = await song_repo.add_song(playlist.id, test_song.id)
        ps2 = await song_repo.add_song(playlist.id, test_song.id)
        ps3 = await song_repo.add_song(playlist.id, test_song.id)
        ps4 = await song_repo.add_song(playlist.id, test_song.id)

        # Move position 4 to position 1
        await song_repo.reorder_song(playlist.id, ps4.id, 1)

        # Verify new order: [4, 1, 2, 3]
        songs = await song_repo.get_songs(playlist.id)
        song_ids = [s['playlist_song_id'] for s in songs]
        assert song_ids == [ps4.id, ps1.id, ps2.id, ps3.id]

    @pytest.mark.asyncio
    async def test_reorder_song_to_first_position(self, db_session: AsyncSession, test_song):
        """
        RED phase - Test moving song to first position
        Task 3.3: Edge case - move to position 1
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

        # Move position 3 to position 1
        await song_repo.reorder_song(playlist.id, ps3.id, 1)

        # Verify new order: [3, 1, 2]
        songs = await song_repo.get_songs(playlist.id)
        song_ids = [s['playlist_song_id'] for s in songs]
        assert song_ids == [ps3.id, ps1.id, ps2.id]

    @pytest.mark.asyncio
    async def test_reorder_song_to_last_position(self, db_session: AsyncSession, test_song):
        """
        RED phase - Test moving song to last position
        Task 3.3: Edge case - move to last position
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

        # Move position 1 to position 3 (last)
        await song_repo.reorder_song(playlist.id, ps1.id, 3)

        # Verify new order: [2, 3, 1]
        songs = await song_repo.get_songs(playlist.id)
        song_ids = [s['playlist_song_id'] for s in songs]
        assert song_ids == [ps2.id, ps3.id, ps1.id]
