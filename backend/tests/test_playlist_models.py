"""
Test Playlist and PlaylistSong models - Task 1.3
Requirements: 1, 4, 5
"""
import pytest
from datetime import datetime
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_playlist_model_creation(db_session: AsyncSession, test_user):
    """
    RED phase - Test Playlist model can be created
    Task 1.3: Define Playlist SQLAlchemy model
    """
    from app.models.playlist import Playlist

    playlist = Playlist(
        title="My Awesome Playlist",
        owner_user_id=test_user.id,
        is_public=False
    )

    db_session.add(playlist)
    await db_session.commit()
    await db_session.refresh(playlist)

    assert playlist.id is not None
    assert playlist.title == "My Awesome Playlist"
    assert playlist.owner_user_id == test_user.id
    assert playlist.is_public == False
    assert isinstance(playlist.created_at, datetime)
    assert isinstance(playlist.updated_at, datetime)


@pytest.mark.asyncio
async def test_playlist_model_relationships(db_session: AsyncSession, test_user):
    """
    RED phase - Test Playlist relationships
    Task 1.3: Verify owner relationship and playlist_songs collection
    """
    from app.models.playlist import Playlist

    playlist = Playlist(
        title="Test Playlist",
        owner_user_id=test_user.id,
        is_public=True
    )

    db_session.add(playlist)
    await db_session.commit()
    await db_session.refresh(playlist, ['owner', 'playlist_songs'])

    # Test owner relationship
    assert playlist.owner is not None
    assert playlist.owner.id == test_user.id
    assert playlist.owner.email == test_user.email

    # Test playlist_songs collection (should be empty initially)
    assert hasattr(playlist, 'playlist_songs')
    assert len(playlist.playlist_songs) == 0


@pytest.mark.asyncio
async def test_playlist_model_repr(db_session: AsyncSession, test_user):
    """
    RED phase - Test Playlist __repr__ method
    Task 1.3: Implement __repr__ for debugging
    """
    from app.models.playlist import Playlist

    playlist = Playlist(
        title="Debug Playlist",
        owner_user_id=test_user.id
    )

    db_session.add(playlist)
    await db_session.commit()
    await db_session.refresh(playlist)

    repr_str = repr(playlist)
    assert "Playlist" in repr_str
    assert str(playlist.id) in repr_str or "Debug Playlist" in repr_str


@pytest.mark.asyncio
async def test_playlist_song_model_creation(db_session: AsyncSession, test_playlist, test_song):
    """
    RED phase - Test PlaylistSong model creation
    Task 1.3: Define PlaylistSong SQLAlchemy model
    """
    from app.models.playlist import PlaylistSong

    playlist_song = PlaylistSong(
        playlist_id=test_playlist.id,
        song_id=test_song.id,
        position=1
    )

    db_session.add(playlist_song)
    await db_session.commit()
    await db_session.refresh(playlist_song)

    assert playlist_song.id is not None
    assert playlist_song.playlist_id == test_playlist.id
    assert playlist_song.song_id == test_song.id
    assert playlist_song.position == 1
    assert isinstance(playlist_song.created_at, datetime)


@pytest.mark.asyncio
async def test_playlist_song_relationships(db_session: AsyncSession, test_playlist, test_song):
    """
    RED phase - Test PlaylistSong relationships
    Task 1.3: Verify playlist and song relationships
    """
    from app.models.playlist import PlaylistSong

    playlist_song = PlaylistSong(
        playlist_id=test_playlist.id,
        song_id=test_song.id,
        position=1
    )

    db_session.add(playlist_song)
    await db_session.commit()
    await db_session.refresh(playlist_song, ['playlist', 'song'])

    # Test playlist relationship
    assert playlist_song.playlist is not None
    assert playlist_song.playlist.id == test_playlist.id
    assert playlist_song.playlist.title == test_playlist.title

    # Test song relationship
    assert playlist_song.song is not None
    assert playlist_song.song.id == test_song.id
    assert playlist_song.song.title == test_song.title


@pytest.mark.asyncio
async def test_playlist_cascade_delete(db_session: AsyncSession, test_user, test_song):
    """
    RED phase - Test CASCADE delete behavior
    Task 1.3: Verify deleting playlist removes all playlist_songs
    Requirement: 4 (Playlist Deletion)
    """
    from app.models.playlist import Playlist, PlaylistSong

    # Create playlist with song
    playlist = Playlist(
        title="Temp Playlist",
        owner_user_id=test_user.id
    )
    db_session.add(playlist)
    await db_session.commit()
    await db_session.refresh(playlist)

    # Add song to playlist
    playlist_song = PlaylistSong(
        playlist_id=playlist.id,
        song_id=test_song.id,
        position=1
    )
    db_session.add(playlist_song)
    await db_session.commit()

    playlist_id = playlist.id
    playlist_song_id = playlist_song.id

    # Delete playlist
    await db_session.delete(playlist)
    await db_session.commit()

    # Verify playlist_song was also deleted (CASCADE)
    result = await db_session.execute(
        select(PlaylistSong).where(PlaylistSong.id == playlist_song_id)
    )
    deleted_playlist_song = result.scalar_one_or_none()

    assert deleted_playlist_song is None, "playlist_song should be CASCADE deleted"


@pytest.mark.asyncio
async def test_playlist_allows_duplicate_songs(db_session: AsyncSession, test_playlist, test_song):
    """
    RED phase - Test duplicate songs allowed
    Task 1.3: Verify no unique constraint on (playlist_id, song_id)
    Requirement: 12 (Duplicate Song Handling)
    """
    from app.models.playlist import PlaylistSong

    # Add same song twice to playlist
    playlist_song_1 = PlaylistSong(
        playlist_id=test_playlist.id,
        song_id=test_song.id,
        position=1
    )
    playlist_song_2 = PlaylistSong(
        playlist_id=test_playlist.id,
        song_id=test_song.id,  # Same song
        position=2
    )

    db_session.add(playlist_song_1)
    db_session.add(playlist_song_2)
    await db_session.commit()

    # Query all playlist_songs for this playlist
    result = await db_session.execute(
        select(PlaylistSong).where(PlaylistSong.playlist_id == test_playlist.id)
    )
    playlist_songs = result.scalars().all()

    assert len(playlist_songs) == 2, "Should allow duplicate songs"
    assert playlist_songs[0].song_id == playlist_songs[1].song_id, "Both should be same song"
    assert playlist_songs[0].id != playlist_songs[1].id, "But different instances (surrogate key)"
