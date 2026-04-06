"""
Test SQLAlchemy Models for Music Catalog - Task 1.4
Test-Driven Development (TDD): RED phase

Tests for Artist, Album, Song models with relationships
Requirements: 12.1, 12.2, 12.3
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime


@pytest.mark.asyncio
async def test_artist_model_import():
    """
    Test that Artist model can be imported

    Requirements:
    - 1.1: Artist model exists
    """
    from app.models.artist import Artist
    assert Artist is not None, "Artist model should be importable"


@pytest.mark.asyncio
async def test_album_model_import():
    """
    Test that Album model can be imported

    Requirements:
    - 5.1: Album model exists
    """
    from app.models.album import Album
    assert Album is not None, "Album model should be importable"


@pytest.mark.asyncio
async def test_song_model_import():
    """
    Test that Song model can be imported

    Requirements:
    - 8.1: Song model exists
    """
    from app.models.song import Song
    assert Song is not None, "Song model should be importable"


@pytest.mark.asyncio
async def test_artist_create_and_query(db_session: AsyncSession):
    """
    Test creating and querying Artist model

    Requirements:
    - 1.1: Create artist record
    - 1.4: Set timestamps automatically
    """
    from app.models.artist import Artist

    # Create artist
    artist = Artist(name="The Beatles", country="GB")
    db_session.add(artist)
    await db_session.commit()
    await db_session.refresh(artist)

    # Verify
    assert artist.id is not None, "Artist ID should be generated"
    assert artist.name == "The Beatles", "Artist name should match"
    assert artist.country == "GB", "Artist country should match"
    assert artist.created_at is not None, "created_at should be set"
    assert artist.updated_at is not None, "updated_at should be set"


@pytest.mark.asyncio
async def test_album_create_with_artist_relationship(db_session: AsyncSession):
    """
    Test creating Album with Artist relationship

    Requirements:
    - 5.1: Create album record
    - 5.3: Validate artist_id exists
    - 12.2: Artist → Albums relationship
    """
    from app.models.artist import Artist
    from app.models.album import Album

    # Create artist first
    artist = Artist(name="Pink Floyd", country="GB")
    db_session.add(artist)
    await db_session.commit()
    await db_session.refresh(artist)

    # Create album
    album = Album(
        title="The Dark Side of the Moon",
        artist_id=artist.id,
        release_year=1973,
        album_cover_url="https://example.com/cover.jpg"
    )
    db_session.add(album)
    await db_session.commit()
    await db_session.refresh(album)

    # Verify
    assert album.id is not None, "Album ID should be generated"
    assert album.title == "The Dark Side of the Moon", "Album title should match"
    assert album.artist_id == artist.id, "Album artist_id should reference artist"
    assert album.release_year == 1973, "Album release_year should match"
    assert album.created_at is not None, "created_at should be set"


@pytest.mark.asyncio
async def test_song_create_with_album_relationship(db_session: AsyncSession):
    """
    Test creating Song with Album relationship

    Requirements:
    - 8.1: Create song record
    - 8.3: Validate album_id exists
    - 12.1: Album → Songs relationship
    """
    from app.models.artist import Artist
    from app.models.album import Album
    from app.models.song import Song

    # Create artist and album first
    artist = Artist(name="Led Zeppelin", country="GB")
    db_session.add(artist)
    await db_session.commit()
    await db_session.refresh(artist)

    album = Album(title="Led Zeppelin IV", artist_id=artist.id, release_year=1971)
    db_session.add(album)
    await db_session.commit()
    await db_session.refresh(album)

    # Create song
    song = Song(
        title="Stairway to Heaven",
        album_id=album.id,
        duration_seconds=482,
        genre="Rock",
        year=1971
    )
    db_session.add(song)
    await db_session.commit()
    await db_session.refresh(song)

    # Verify
    assert song.id is not None, "Song ID should be generated"
    assert song.title == "Stairway to Heaven", "Song title should match"
    assert song.album_id == album.id, "Song album_id should reference album"
    assert song.duration_seconds == 482, "Song duration should match"
    assert song.deleted_at is None, "Song should not be soft deleted by default"
    assert song.created_at is not None, "created_at should be set"


@pytest.mark.asyncio
async def test_artist_albums_relationship(db_session: AsyncSession):
    """
    Test that Artist has albums relationship

    Requirements:
    - 12.2: Artist → Albums one-to-many relationship
    """
    from app.models.artist import Artist
    from app.models.album import Album

    # Create artist with albums
    artist = Artist(name="Queen", country="GB")
    db_session.add(artist)
    await db_session.commit()
    await db_session.refresh(artist)

    album1 = Album(title="A Night at the Opera", artist_id=artist.id, release_year=1975)
    album2 = Album(title="News of the World", artist_id=artist.id, release_year=1977)
    db_session.add_all([album1, album2])
    await db_session.commit()

    # Query artist with albums (using eager loading)
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    result = await db_session.execute(
        select(Artist).where(Artist.id == artist.id).options(selectinload(Artist.albums))
    )
    artist_with_albums = result.scalar_one()

    # Verify relationship
    assert len(artist_with_albums.albums) == 2, "Artist should have 2 albums"
    assert artist_with_albums.albums[0].title in ["A Night at the Opera", "News of the World"]


@pytest.mark.asyncio
async def test_album_songs_relationship(db_session: AsyncSession):
    """
    Test that Album has songs relationship

    Requirements:
    - 12.1: Album → Songs one-to-many relationship
    """
    from app.models.artist import Artist
    from app.models.album import Album
    from app.models.song import Song

    # Create artist, album, and songs
    artist = Artist(name="AC/DC", country="AU")
    db_session.add(artist)
    await db_session.commit()
    await db_session.refresh(artist)

    album = Album(title="Back in Black", artist_id=artist.id, release_year=1980)
    db_session.add(album)
    await db_session.commit()
    await db_session.refresh(album)

    song1 = Song(title="Hells Bells", album_id=album.id, duration_seconds=312)
    song2 = Song(title="Back in Black", album_id=album.id, duration_seconds=255)
    db_session.add_all([song1, song2])
    await db_session.commit()

    # Query album with songs
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    result = await db_session.execute(
        select(Album).where(Album.id == album.id).options(selectinload(Album.songs))
    )
    album_with_songs = result.scalar_one()

    # Verify relationship
    assert len(album_with_songs.songs) == 2, "Album should have 2 songs"
    assert album_with_songs.songs[0].title in ["Hells Bells", "Back in Black"]


@pytest.mark.asyncio
async def test_song_soft_delete_field(db_session: AsyncSession):
    """
    Test that Song model has deleted_at field for soft delete

    Requirements:
    - 11.1: Soft delete with deleted_at timestamp
    """
    from app.models.song import Song
    from app.models.artist import Artist
    from app.models.album import Album

    # Create artist, album, song
    artist = Artist(name="Test Artist", country="US")
    db_session.add(artist)
    await db_session.commit()
    await db_session.refresh(artist)

    album = Album(title="Test Album", artist_id=artist.id, release_year=2020)
    db_session.add(album)
    await db_session.commit()
    await db_session.refresh(album)

    song = Song(title="Test Song", album_id=album.id, duration_seconds=180)
    db_session.add(song)
    await db_session.commit()
    await db_session.refresh(song)

    # Verify soft delete field
    assert song.deleted_at is None, "Song should not be deleted initially"

    # Soft delete
    song.deleted_at = datetime.utcnow()
    await db_session.commit()
    await db_session.refresh(song)

    assert song.deleted_at is not None, "Song should have deleted_at timestamp after soft delete"
