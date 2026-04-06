"""
Test PlaylistRepository for data access - Task 3.1
Test-Driven Development (TDD): RED-GREEN phases

Requirements: 1, 2, 3, 4, 8
"""
import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession


class TestPlaylistRepositoryBaseCRUD:
    """Test base CRUD methods - Task 3.1"""

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
    async def test_playlist_repository_create(self, db_session: AsyncSession):
        """
        RED phase - Test PlaylistRepository.create with title, owner_user_id, is_public
        Task 3.1: Implement create method inserting playlist record with timestamps
        Requirement: 1 (Playlist Creation)
        """
        from app.repositories.playlist_repository import PlaylistRepository

        user = await self._create_test_user(db_session)
        repo = PlaylistRepository(db_session)

        playlist = await repo.create(
            title="Test Playlist",
            owner_user_id=user.id,
            is_public=False
        )

        assert playlist.id is not None
        assert playlist.title == "Test Playlist"
        assert playlist.owner_user_id == user.id
        assert playlist.is_public == False
        assert isinstance(playlist.created_at, datetime)
        assert isinstance(playlist.updated_at, datetime)

    @pytest.mark.asyncio
    async def test_playlist_repository_create_public(self, db_session: AsyncSession):
        """
        RED phase - Test creating public playlist
        Task 3.1: Create method should support is_public parameter
        Requirement: 8 (Privacy Control)
        """
        from app.repositories.playlist_repository import PlaylistRepository

        user = await self._create_test_user(db_session)
        repo = PlaylistRepository(db_session)

        playlist = await repo.create(
            title="Public Playlist",
            owner_user_id=user.id,
            is_public=True
        )

        assert playlist.is_public == True

    @pytest.mark.asyncio
    async def test_playlist_repository_get_by_id(self, db_session: AsyncSession):
        """
        RED phase - Test PlaylistRepository.get_by_id with eager loading
        Task 3.1: Implement get_by_id method with selectinload for playlist_songs
        Requirement: 2 (Playlist Retrieval)
        """
        from app.repositories.playlist_repository import PlaylistRepository

        user = await self._create_test_user(db_session)
        repo = PlaylistRepository(db_session)

        # Create playlist
        created = await repo.create("Test Playlist", user.id, False)

        # Get by ID
        playlist = await repo.get_by_id(created.id)

        assert playlist is not None
        assert playlist.id == created.id
        assert playlist.title == created.title
        assert playlist.owner_user_id == user.id

    @pytest.mark.asyncio
    async def test_playlist_repository_get_by_id_not_found(self, db_session: AsyncSession):
        """
        RED phase - Test get_by_id with non-existent ID returns None
        Task 3.1: get_by_id should return None if not found
        """
        from app.repositories.playlist_repository import PlaylistRepository

        repo = PlaylistRepository(db_session)

        playlist = await repo.get_by_id(999999)

        assert playlist is None

    @pytest.mark.asyncio
    async def test_playlist_repository_get_by_owner(self, db_session: AsyncSession):
        """
        RED phase - Test PlaylistRepository.get_by_owner with pagination
        Task 3.1: Implement get_by_owner querying WHERE owner_user_id = ? with LIMIT/OFFSET
        Requirement: 2 (Playlist Retrieval)
        """
        from app.repositories.playlist_repository import PlaylistRepository

        user = await self._create_test_user(db_session)
        repo = PlaylistRepository(db_session)

        # Create playlists
        await repo.create("Playlist 1", user.id, False)
        await repo.create("Playlist 2", user.id, False)
        await repo.create("Playlist 3", user.id, True)

        # Get first page (default page_size=20)
        playlists, total = await repo.get_by_owner(user.id, page=1, page_size=20)

        assert total == 3
        assert len(playlists) == 3
        assert all(p.owner_user_id == user.id for p in playlists)

    @pytest.mark.asyncio
    async def test_playlist_repository_get_by_owner_pagination(self, db_session: AsyncSession):
        """
        RED phase - Test pagination with get_by_owner
        Task 3.1: Verify LIMIT/OFFSET pagination works correctly
        """
        from app.repositories.playlist_repository import PlaylistRepository

        user = await self._create_test_user(db_session)
        repo = PlaylistRepository(db_session)

        # Create 5 playlists
        for i in range(5):
            await repo.create(f"Playlist {i+1}", user.id, False)

        # Get page 1 with page_size=2
        playlists_p1, total = await repo.get_by_owner(user.id, page=1, page_size=2)
        assert total == 5
        assert len(playlists_p1) == 2

        # Get page 2 with page_size=2
        playlists_p2, total = await repo.get_by_owner(user.id, page=2, page_size=2)
        assert len(playlists_p2) == 2

        # Verify no overlap
        p1_ids = {p.id for p in playlists_p1}
        p2_ids = {p.id for p in playlists_p2}
        assert p1_ids.isdisjoint(p2_ids)

    @pytest.mark.asyncio
    async def test_playlist_repository_get_public(self, db_session: AsyncSession):
        """
        RED phase - Test PlaylistRepository.get_public with pagination
        Task 3.1: Implement get_public querying WHERE is_public = TRUE
        Requirement: 2, 8 (Public Playlist Retrieval)
        """
        from app.repositories.playlist_repository import PlaylistRepository

        user = await self._create_test_user(db_session)
        repo = PlaylistRepository(db_session)

        # Create mix of public and private playlists
        await repo.create("Private 1", user.id, False)
        await repo.create("Public 1", user.id, True)
        await repo.create("Private 2", user.id, False)
        await repo.create("Public 2", user.id, True)
        await repo.create("Public 3", user.id, True)

        # Get public playlists
        playlists, total = await repo.get_public(page=1, page_size=20)

        assert total == 3
        assert len(playlists) == 3
        assert all(p.is_public == True for p in playlists)

    @pytest.mark.asyncio
    async def test_playlist_repository_update(self, db_session: AsyncSession):
        """
        RED phase - Test PlaylistRepository.update with optional fields
        Task 3.1: Implement update method updating fields and updated_at timestamp
        Requirement: 3 (Playlist Update)
        """
        from app.repositories.playlist_repository import PlaylistRepository

        user = await self._create_test_user(db_session)
        repo = PlaylistRepository(db_session)

        # Create playlist
        playlist = await repo.create("Original Title", user.id, False)
        original_updated_at = playlist.updated_at

        # Update title only
        updated = await repo.update(playlist.id, title="Updated Title")

        assert updated.title == "Updated Title"
        assert updated.updated_at > original_updated_at

    @pytest.mark.asyncio
    async def test_playlist_repository_update_privacy(self, db_session: AsyncSession):
        """
        RED phase - Test updating is_public field
        Task 3.1: Update method should support optional is_public
        Requirement: 8 (Privacy Control)
        """
        from app.repositories.playlist_repository import PlaylistRepository

        user = await self._create_test_user(db_session)
        repo = PlaylistRepository(db_session)

        # Create private playlist
        playlist = await repo.create("Test Playlist", user.id, False)
        assert playlist.is_public == False

        # Toggle privacy
        updated = await repo.update(playlist.id, is_public=True)

        assert updated.is_public == True

    @pytest.mark.asyncio
    async def test_playlist_repository_update_both_fields(self, db_session: AsyncSession):
        """
        RED phase - Test updating both title and is_public
        Task 3.1: Update should support updating multiple fields
        """
        from app.repositories.playlist_repository import PlaylistRepository

        user = await self._create_test_user(db_session)
        repo = PlaylistRepository(db_session)

        # Create playlist
        playlist = await repo.create("Original", user.id, False)

        # Update both fields
        updated = await repo.update(
            playlist.id,
            title="New Title",
            is_public=True
        )

        assert updated.title == "New Title"
        assert updated.is_public == True

    @pytest.mark.asyncio
    async def test_playlist_repository_delete(self, db_session: AsyncSession):
        """
        RED phase - Test PlaylistRepository.delete performing hard delete
        Task 3.1: Implement delete method removing playlist record
        Requirement: 4 (Playlist Deletion)
        """
        from app.repositories.playlist_repository import PlaylistRepository

        user = await self._create_test_user(db_session)
        repo = PlaylistRepository(db_session)

        # Create playlist
        playlist = await repo.create("To Delete", user.id, False)
        playlist_id = playlist.id

        # Delete playlist
        result = await repo.delete(playlist_id)
        assert result == True

        # Verify deleted
        deleted_playlist = await repo.get_by_id(playlist_id)
        assert deleted_playlist is None

    @pytest.mark.asyncio
    async def test_playlist_repository_delete_cascades_to_songs(self, db_session: AsyncSession, test_song):
        """
        RED phase - Test CASCADE deletes playlist_songs automatically
        Task 3.1: Verify CASCADE deletion removes playlist_songs entries
        Requirement: 4 (Playlist Deletion)
        """
        from app.repositories.playlist_repository import PlaylistRepository
        from app.repositories.playlist_song_repository import PlaylistSongRepository
        from sqlalchemy import select
        from app.models.playlist import PlaylistSong

        user = await self._create_test_user(db_session)
        playlist_repo = PlaylistRepository(db_session)
        song_repo = PlaylistSongRepository(db_session)

        # Create playlist
        playlist = await playlist_repo.create("Test Playlist", user.id, False)

        # Add song to playlist
        await song_repo.add_song(playlist.id, test_song.id)

        # Verify song added
        result = await db_session.execute(
            select(PlaylistSong).where(PlaylistSong.playlist_id == playlist.id)
        )
        playlist_songs = result.scalars().all()
        assert len(playlist_songs) == 1

        # Delete playlist
        await playlist_repo.delete(playlist.id)

        # Verify playlist_songs CASCADE deleted
        result = await db_session.execute(
            select(PlaylistSong).where(PlaylistSong.playlist_id == playlist.id)
        )
        playlist_songs = result.scalars().all()
        assert len(playlist_songs) == 0
