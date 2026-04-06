"""
Test Referential Integrity and Cascade Behavior - Task 12
Test-Driven Development (TDD)

Tests for foreign key constraints and cascade behavior
Requirements: 12.1, 12.2, 12.3
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.models.artist import Artist
from app.models.album import Album
from app.models.song import Song


@pytest.mark.asyncio
async def test_delete_album_cascades_to_songs(db_session: AsyncSession):
    """
    Test that deleting an album cascades to all associated songs (hard delete)

    Requirements:
    - 12.1: DELETE album removes all associated songs
    - Verify CASCADE behavior on album → songs foreign key
    """
    # Create artist
    artist = Artist(name="Test Artist", country="US")
    db_session.add(artist)
    await db_session.commit()
    await db_session.refresh(artist)

    # Create album
    album = Album(
        title="Test Album",
        artist_id=artist.id,
        release_year=2020
    )
    db_session.add(album)
    await db_session.commit()
    await db_session.refresh(album)

    # Create songs
    song1 = Song(
        title="Song 1",
        album_id=album.id,
        duration_seconds=180
    )
    song2 = Song(
        title="Song 2",
        album_id=album.id,
        duration_seconds=200
    )
    db_session.add(song1)
    db_session.add(song2)
    await db_session.commit()
    await db_session.refresh(song1)
    await db_session.refresh(song2)

    song1_id = song1.id
    song2_id = song2.id
    album_id = album.id

    # Delete album
    await db_session.delete(album)
    await db_session.commit()

    # Verify songs were cascade deleted
    from sqlalchemy import select
    result = await db_session.execute(
        select(Song).where(Song.id.in_([song1_id, song2_id]))
    )
    remaining_songs = result.scalars().all()

    assert len(remaining_songs) == 0, "Songs should be cascade deleted when album is deleted"

    # Verify album is deleted
    result = await db_session.execute(
        select(Album).where(Album.id == album_id)
    )
    deleted_album = result.scalar_one_or_none()
    assert deleted_album is None, "Album should be deleted"


@pytest.mark.asyncio
async def test_delete_artist_with_albums_cascades_albums(db_session: AsyncSession):
    """
    Test that deleting an artist cascades to albums due to SQLAlchemy cascade

    Requirements:
    - 12.2: DELETE artist behavior with albums
    - Note: SQLAlchemy cascade="all, delete" causes albums to be deleted first
    """
    # Create artist
    artist = Artist(name="Test Artist", country="BR")
    db_session.add(artist)
    await db_session.commit()
    await db_session.refresh(artist)

    # Create album
    album = Album(
        title="Test Album",
        artist_id=artist.id,
        release_year=2021
    )
    db_session.add(album)
    await db_session.commit()
    await db_session.refresh(album)

    album_id = album.id
    artist_id = artist.id

    # Delete artist - SQLAlchemy will cascade delete albums
    await db_session.delete(artist)
    await db_session.commit()

    # Verify artist is deleted
    from sqlalchemy import select
    result = await db_session.execute(
        select(Artist).where(Artist.id == artist_id)
    )
    deleted_artist = result.scalar_one_or_none()
    assert deleted_artist is None, "Artist should be deleted"

    # Verify album is also deleted (cascaded by SQLAlchemy)
    result = await db_session.execute(
        select(Album).where(Album.id == album_id)
    )
    deleted_album = result.scalar_one_or_none()
    assert deleted_album is None, "Album should be cascade deleted due to SQLAlchemy cascade"


@pytest.mark.asyncio
async def test_delete_artist_without_albums_succeeds(db_session: AsyncSession):
    """
    Test that deleting an artist without albums succeeds

    Requirements:
    - 12.2: DELETE artist without albums should succeed
    """
    # Create artist without albums
    artist = Artist(name="Lonely Artist", country="JP")
    db_session.add(artist)
    await db_session.commit()
    await db_session.refresh(artist)

    artist_id = artist.id

    # Delete artist - should succeed
    await db_session.delete(artist)
    await db_session.commit()

    # Verify artist is deleted
    from sqlalchemy import select
    result = await db_session.execute(
        select(Artist).where(Artist.id == artist_id)
    )
    deleted_artist = result.scalar_one_or_none()

    assert deleted_artist is None, "Artist without albums should be deletable"


@pytest.mark.asyncio
async def test_create_album_with_invalid_artist_id_fails(db_session: AsyncSession):
    """
    Test that creating an album with non-existent artist_id raises IntegrityError

    Requirements:
    - 12.3: Foreign key validation on album creation
    """
    # Try to create album with invalid artist_id
    album = Album(
        title="Orphan Album",
        artist_id=999999,  # Non-existent artist
        release_year=2022
    )
    db_session.add(album)

    with pytest.raises(IntegrityError) as exc_info:
        await db_session.commit()

    assert "foreign key constraint" in str(exc_info.value).lower() or \
           "violates foreign key" in str(exc_info.value).lower(), \
           "Should raise IntegrityError for invalid artist_id"

    await db_session.rollback()


@pytest.mark.asyncio
async def test_create_song_with_invalid_album_id_fails(db_session: AsyncSession):
    """
    Test that creating a song with non-existent album_id raises IntegrityError

    Requirements:
    - 12.3: Foreign key validation on song creation
    """
    # Try to create song with invalid album_id
    song = Song(
        title="Orphan Song",
        album_id=999999,  # Non-existent album
        duration_seconds=180
    )
    db_session.add(song)

    with pytest.raises(IntegrityError) as exc_info:
        await db_session.commit()

    assert "foreign key constraint" in str(exc_info.value).lower() or \
           "violates foreign key" in str(exc_info.value).lower(), \
           "Should raise IntegrityError for invalid album_id"

    await db_session.rollback()


@pytest.mark.asyncio
async def test_cascade_deletion_with_soft_deleted_songs(db_session: AsyncSession):
    """
    Test that cascade deletion works with both active and soft-deleted songs

    Requirements:
    - 12.1: CASCADE should remove all songs (including soft-deleted)
    - 11.2: Soft delete should not affect cascade behavior
    """
    from datetime import datetime

    # Create artist and album
    artist = Artist(name="Cascade Artist", country="FR")
    db_session.add(artist)
    await db_session.commit()
    await db_session.refresh(artist)

    album = Album(
        title="Cascade Album",
        artist_id=artist.id,
        release_year=2023
    )
    db_session.add(album)
    await db_session.commit()
    await db_session.refresh(album)

    # Create active and soft-deleted songs
    active_song = Song(
        title="Active Song",
        album_id=album.id,
        duration_seconds=180
    )
    deleted_song = Song(
        title="Deleted Song",
        album_id=album.id,
        duration_seconds=200,
        deleted_at=datetime.utcnow()
    )
    db_session.add(active_song)
    db_session.add(deleted_song)
    await db_session.commit()

    active_song_id = active_song.id
    deleted_song_id = deleted_song.id

    # Delete album
    await db_session.delete(album)
    await db_session.commit()

    # Verify both songs are cascade deleted
    from sqlalchemy import select
    result = await db_session.execute(
        select(Song).where(Song.id.in_([active_song_id, deleted_song_id]))
    )
    remaining_songs = result.scalars().all()

    assert len(remaining_songs) == 0, "Both active and soft-deleted songs should be cascade deleted"


@pytest.mark.asyncio
async def test_null_foreign_key_not_allowed(db_session: AsyncSession):
    """
    Test that NULL values are not allowed for foreign key columns

    Requirements:
    - 12.3: Foreign keys must be NOT NULL
    """
    # Try to create album with NULL artist_id
    album = Album(
        title="Album Without Artist",
        artist_id=None,
        release_year=2020
    )
    db_session.add(album)

    with pytest.raises(IntegrityError) as exc_info:
        await db_session.commit()

    assert "not null" in str(exc_info.value).lower() or \
           "null value" in str(exc_info.value).lower(), \
           "Should raise IntegrityError for NULL artist_id"

    await db_session.rollback()

    # Create valid artist for song test
    artist = Artist(name="Test Artist", country="US")
    db_session.add(artist)
    await db_session.commit()
    await db_session.refresh(artist)

    album_valid = Album(
        title="Valid Album",
        artist_id=artist.id,
        release_year=2020
    )
    db_session.add(album_valid)
    await db_session.commit()
    await db_session.refresh(album_valid)

    # Try to create song with NULL album_id
    song = Song(
        title="Song Without Album",
        album_id=None,
        duration_seconds=180
    )
    db_session.add(song)

    with pytest.raises(IntegrityError) as exc_info:
        await db_session.commit()

    assert "not null" in str(exc_info.value).lower() or \
           "null value" in str(exc_info.value).lower(), \
           "Should raise IntegrityError for NULL album_id"

    await db_session.rollback()
