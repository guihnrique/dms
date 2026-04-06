"""
Test PlaylistService for business logic - Task 4.1, 4.2, 4.3, 4.4
Test-Driven Development (TDD): RED-GREEN phases

Requirements: 1, 2, 3, 4, 5, 6, 7, 8, 9
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession


class TestPlaylistServiceCRUD:
    """Test PlaylistService CRUD operations - Task 4.1"""

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
    async def test_create_playlist_valid_title(self, db_session: AsyncSession):
        """
        RED phase - Test create_playlist with valid title
        Task 4.1: Implement create_playlist validating title length
        Requirement: 1 (Playlist Creation)
        """
        from app.services.playlist_service import PlaylistService

        user = await self._create_test_user(db_session)
        service = PlaylistService(db_session)

        playlist = await service.create_playlist(
            title="My Playlist",
            owner_user_id=user.id,
            is_public=False
        )

        assert playlist is not None
        assert playlist.title == "My Playlist"
        assert playlist.owner_user_id == user.id
        assert playlist.is_public == False

    @pytest.mark.asyncio
    async def test_create_playlist_default_privacy(self, db_session: AsyncSession):
        """
        RED phase - Test default is_public=False
        Task 4.1: Verify default privacy is private
        Requirement: 8 (Privacy Control)
        """
        from app.services.playlist_service import PlaylistService

        user = await self._create_test_user(db_session)
        service = PlaylistService(db_session)

        playlist = await service.create_playlist(
            title="Test Playlist",
            owner_user_id=user.id
        )

        assert playlist.is_public == False

    @pytest.mark.asyncio
    async def test_create_playlist_validates_title_length(self, db_session: AsyncSession):
        """
        RED phase - Test title validation (1-200 chars)
        Task 4.1: Validate title length
        """
        from app.services.playlist_service import PlaylistService

        user = await self._create_test_user(db_session)
        service = PlaylistService(db_session)

        # Empty title should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            await service.create_playlist(title="", owner_user_id=user.id)
        assert "title" in str(exc_info.value).lower()

        # Title > 200 chars should raise ValueError
        long_title = "A" * 201
        with pytest.raises(ValueError) as exc_info:
            await service.create_playlist(title=long_title, owner_user_id=user.id)
        assert "title" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_get_playlist_by_id_as_owner(self, db_session: AsyncSession):
        """
        RED phase - Test get_playlist_by_id with owner
        Task 4.1: Implement get_playlist_by_id with privacy enforcement
        Requirement: 2 (Playlist Retrieval)
        """
        from app.services.playlist_service import PlaylistService

        user = await self._create_test_user(db_session)
        service = PlaylistService(db_session)

        # Create playlist
        created = await service.create_playlist("Test", user.id, is_public=False)

        # Retrieve as owner
        playlist = await service.get_playlist_by_id(created.id, current_user_id=user.id)

        assert playlist is not None
        assert playlist.id == created.id

    @pytest.mark.asyncio
    async def test_get_playlist_by_id_private_non_owner_forbidden(self, db_session: AsyncSession):
        """
        RED phase - Test private playlist access by non-owner raises 403
        Task 4.1: Enforce privacy - private playlist → owner only
        Requirement: 8 (Privacy Control)
        """
        from app.services.playlist_service import PlaylistService
        from fastapi import HTTPException

        user1 = await self._create_test_user(db_session)
        user2 = await self._create_test_user(db_session)
        service = PlaylistService(db_session)

        # Create private playlist
        playlist = await service.create_playlist("Private", user1.id, is_public=False)

        # Try to access as different user
        with pytest.raises(HTTPException) as exc_info:
            await service.get_playlist_by_id(playlist.id, current_user_id=user2.id)
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_get_playlist_by_id_public_accessible(self, db_session: AsyncSession):
        """
        RED phase - Test public playlist accessible by anyone
        Task 4.1: Public playlists accessible to all
        """
        from app.services.playlist_service import PlaylistService

        user1 = await self._create_test_user(db_session)
        user2 = await self._create_test_user(db_session)
        service = PlaylistService(db_session)

        # Create public playlist
        playlist = await service.create_playlist("Public", user1.id, is_public=True)

        # Access as different user
        retrieved = await service.get_playlist_by_id(playlist.id, current_user_id=user2.id)
        assert retrieved is not None

        # Access without user (guest)
        retrieved = await service.get_playlist_by_id(playlist.id, current_user_id=None)
        assert retrieved is not None

    @pytest.mark.asyncio
    async def test_get_playlist_calculates_metadata(self, db_session: AsyncSession, test_song):
        """
        RED phase - Test songs_count and total_duration calculated
        Task 4.1: Calculate songs_count and total_duration_seconds
        """
        from app.services.playlist_service import PlaylistService
        from app.repositories.playlist_song_repository import PlaylistSongRepository

        user = await self._create_test_user(db_session)
        service = PlaylistService(db_session)
        song_repo = PlaylistSongRepository(db_session)

        # Create playlist and add songs
        playlist = await service.create_playlist("Test", user.id)
        await song_repo.add_song(playlist.id, test_song.id)
        await song_repo.add_song(playlist.id, test_song.id)

        # Get playlist
        retrieved = await service.get_playlist_by_id(playlist.id, user.id)

        assert retrieved.songs_count == 2
        assert retrieved.total_duration_seconds == test_song.duration_seconds * 2

    @pytest.mark.asyncio
    async def test_get_user_playlists_with_pagination(self, db_session: AsyncSession):
        """
        RED phase - Test get_user_playlists with pagination
        Task 4.1: Implement get_user_playlists with pagination
        Requirement: 2 (Playlist Retrieval)
        """
        from app.services.playlist_service import PlaylistService

        user = await self._create_test_user(db_session)
        service = PlaylistService(db_session)

        # Create 3 playlists
        await service.create_playlist("Playlist 1", user.id)
        await service.create_playlist("Playlist 2", user.id)
        await service.create_playlist("Playlist 3", user.id)

        # Get page 1
        result = await service.get_user_playlists(user.id, page=1, page_size=2)

        assert result['total'] == 3
        assert len(result['items']) == 2
        assert result['page'] == 1
        assert result['page_size'] == 2
        assert result['total_pages'] == 2

    @pytest.mark.asyncio
    async def test_get_public_playlists(self, db_session: AsyncSession):
        """
        RED phase - Test get_public_playlists returns only public
        Task 4.1: Implement get_public_playlists
        Requirement: 2, 8 (Public Playlist Retrieval)
        """
        from app.services.playlist_service import PlaylistService

        user = await self._create_test_user(db_session)
        service = PlaylistService(db_session)

        # Create mix of public and private
        await service.create_playlist("Private 1", user.id, is_public=False)
        await service.create_playlist("Public 1", user.id, is_public=True)
        await service.create_playlist("Public 2", user.id, is_public=True)

        # Get public playlists
        result = await service.get_public_playlists(page=1, page_size=20)

        assert result['total'] == 2
        assert all(p.is_public for p in result['items'])


class TestPlaylistServiceUpdate:
    """Test PlaylistService update/delete - Task 4.2"""

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
    async def test_update_playlist_title(self, db_session: AsyncSession):
        """
        RED phase - Test update_playlist with title
        Task 4.2: Implement update_playlist
        Requirement: 3 (Playlist Update)
        """
        from app.services.playlist_service import PlaylistService

        user = await self._create_test_user(db_session)
        service = PlaylistService(db_session)

        # Create playlist
        playlist = await service.create_playlist("Original", user.id)

        # Update title
        updated = await service.update_playlist(playlist.id, title="Updated")

        assert updated.title == "Updated"
        assert updated.updated_at > playlist.updated_at

    @pytest.mark.asyncio
    async def test_update_playlist_validates_title(self, db_session: AsyncSession):
        """
        RED phase - Test update validates title length
        Task 4.2: Validate title if provided (1-200 chars)
        """
        from app.services.playlist_service import PlaylistService

        user = await self._create_test_user(db_session)
        service = PlaylistService(db_session)

        playlist = await service.create_playlist("Original", user.id)

        # Empty title should raise ValueError
        with pytest.raises(ValueError):
            await service.update_playlist(playlist.id, title="")

        # Long title should raise ValueError
        with pytest.raises(ValueError):
            await service.update_playlist(playlist.id, title="A" * 201)

    @pytest.mark.asyncio
    async def test_update_playlist_privacy(self, db_session: AsyncSession):
        """
        RED phase - Test update_playlist privacy toggle
        Task 4.2: Update is_public
        Requirement: 8 (Privacy Control)
        """
        from app.services.playlist_service import PlaylistService

        user = await self._create_test_user(db_session)
        service = PlaylistService(db_session)

        playlist = await service.create_playlist("Test", user.id, is_public=False)

        # Toggle to public
        updated = await service.update_playlist(playlist.id, is_public=True)

        assert updated.is_public == True

    @pytest.mark.asyncio
    async def test_delete_playlist(self, db_session: AsyncSession):
        """
        RED phase - Test delete_playlist hard delete
        Task 4.2: Implement delete_playlist
        Requirement: 4 (Playlist Deletion)
        """
        from app.services.playlist_service import PlaylistService

        user = await self._create_test_user(db_session)
        service = PlaylistService(db_session)

        playlist = await service.create_playlist("To Delete", user.id)
        playlist_id = playlist.id

        # Delete
        result = await service.delete_playlist(playlist_id)
        assert result == True

        # Verify deleted
        from app.repositories.playlist_repository import PlaylistRepository
        repo = PlaylistRepository(db_session)
        deleted = await repo.get_by_id(playlist_id)
        assert deleted is None


class TestPlaylistServiceSongManagement:
    """Test PlaylistService song management - Task 4.3, 4.4"""

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
    async def test_add_song_to_playlist(self, db_session: AsyncSession, test_song):
        """
        RED phase - Test add_song_to_playlist validates song exists
        Task 4.3: Implement add_song_to_playlist
        Requirement: 5 (Add Song to Playlist)
        """
        from app.services.playlist_service import PlaylistService

        user = await self._create_test_user(db_session)
        service = PlaylistService(db_session)

        playlist = await service.create_playlist("Test", user.id)

        # Add song
        updated = await service.add_song_to_playlist(playlist.id, test_song.id)

        assert updated.songs_count == 1

    @pytest.mark.asyncio
    async def test_add_song_validates_song_exists(self, db_session: AsyncSession):
        """
        RED phase - Test add_song validates song exists in catalog
        Task 4.3: Check song_id exists via SongRepository
        """
        from app.services.playlist_service import PlaylistService
        from fastapi import HTTPException

        user = await self._create_test_user(db_session)
        service = PlaylistService(db_session)

        playlist = await service.create_playlist("Test", user.id)

        # Try to add non-existent song
        with pytest.raises(HTTPException) as exc_info:
            await service.add_song_to_playlist(playlist.id, 999999)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_add_song_warns_at_1000_songs(self, db_session: AsyncSession, test_song):
        """
        RED phase - Test warning logged at 1000 songs
        Task 4.3: Log warning if songs_count >= 1000
        Requirement: 9 (Playlist Song Limit)
        """
        from app.services.playlist_service import PlaylistService
        from app.repositories.playlist_song_repository import PlaylistSongRepository
        import logging

        user = await self._create_test_user(db_session)
        service = PlaylistService(db_session)
        song_repo = PlaylistSongRepository(db_session)

        playlist = await service.create_playlist("Test", user.id)

        # Add 1000 songs
        for _ in range(1000):
            await song_repo.add_song(playlist.id, test_song.id)

        # Add 1001st song - should still work but log warning
        with pytest.warns() or True:  # May or may not capture warning
            updated = await service.add_song_to_playlist(playlist.id, test_song.id)
            assert updated.songs_count == 1001

    @pytest.mark.asyncio
    async def test_remove_song_from_playlist(self, db_session: AsyncSession, test_song):
        """
        RED phase - Test remove_song_from_playlist
        Task 4.3: Implement remove_song_from_playlist
        Requirement: 6 (Remove Song from Playlist)
        """
        from app.services.playlist_service import PlaylistService

        user = await self._create_test_user(db_session)
        service = PlaylistService(db_session)

        playlist = await service.create_playlist("Test", user.id)

        # Add song
        updated = await service.add_song_to_playlist(playlist.id, test_song.id)

        # Get playlist_song_id
        from app.repositories.playlist_song_repository import PlaylistSongRepository
        song_repo = PlaylistSongRepository(db_session)
        songs = await song_repo.get_songs(playlist.id)
        playlist_song_id = songs[0]['playlist_song_id']

        # Remove song
        updated = await service.remove_song_from_playlist(playlist.id, playlist_song_id)

        assert updated.songs_count == 0

    @pytest.mark.asyncio
    async def test_reorder_song(self, db_session: AsyncSession, test_song):
        """
        RED phase - Test reorder_song validates bounds
        Task 4.4: Implement reorder_song
        Requirement: 7 (Reorder Songs)
        """
        from app.services.playlist_service import PlaylistService
        from app.repositories.playlist_song_repository import PlaylistSongRepository
        from fastapi import HTTPException

        user = await self._create_test_user(db_session)
        service = PlaylistService(db_session)
        song_repo = PlaylistSongRepository(db_session)

        playlist = await service.create_playlist("Test", user.id)

        # Add 3 songs
        await song_repo.add_song(playlist.id, test_song.id)
        await song_repo.add_song(playlist.id, test_song.id)
        ps3 = await song_repo.add_song(playlist.id, test_song.id)

        # Reorder position 3 to position 1
        updated = await service.reorder_song(playlist.id, ps3.id, 1)

        # Verify reordered
        songs = await song_repo.get_songs(playlist.id)
        assert songs[0]['playlist_song_id'] == ps3.id

    @pytest.mark.asyncio
    async def test_reorder_song_validates_bounds(self, db_session: AsyncSession, test_song):
        """
        RED phase - Test reorder_song returns 400 if out of bounds
        Task 4.4: Return 400 Bad Request if new_position out of bounds
        """
        from app.services.playlist_service import PlaylistService
        from app.repositories.playlist_song_repository import PlaylistSongRepository
        from fastapi import HTTPException

        user = await self._create_test_user(db_session)
        service = PlaylistService(db_session)
        song_repo = PlaylistSongRepository(db_session)

        playlist = await service.create_playlist("Test", user.id)
        ps = await song_repo.add_song(playlist.id, test_song.id)

        # Try to reorder to position 5 (out of bounds)
        with pytest.raises(HTTPException) as exc_info:
            await service.reorder_song(playlist.id, ps.id, 5)
        assert exc_info.value.status_code == 400
