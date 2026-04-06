"""
Test Integration and System Testing - Task 13
Test-Driven Development (TDD)

Integration tests for complete catalog workflows
Requirements: 13.1, 13.2, 13.3, 13.4
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from app.models.artist import Artist
from app.models.album import Album
from app.models.song import Song


@pytest.mark.asyncio
async def test_catalog_workflow_create_artist_album_song(db_session: AsyncSession):
    """
    Test complete catalog workflow: create artist → album → song

    Requirements:
    - 13.1: End-to-end catalog creation workflow
    - Verify all relationships and timestamps
    """
    # Step 1: Create artist
    artist = Artist(name="Integration Artist", country="US")
    db_session.add(artist)
    await db_session.commit()
    await db_session.refresh(artist)

    assert artist.id is not None, "Artist should have ID after commit"
    assert artist.created_at is not None, "Artist should have created_at timestamp"
    assert artist.updated_at is not None, "Artist should have updated_at timestamp"

    # Step 2: Create album for artist
    album = Album(
        title="Integration Album",
        artist_id=artist.id,
        release_year=2024,
        album_cover_url="https://example.com/cover.jpg"
    )
    db_session.add(album)
    await db_session.commit()
    await db_session.refresh(album)

    assert album.id is not None, "Album should have ID after commit"
    assert album.artist_id == artist.id, "Album should reference correct artist"
    assert album.created_at is not None, "Album should have created_at timestamp"

    # Step 3: Create songs for album
    song1 = Song(
        title="Integration Song 1",
        album_id=album.id,
        duration_seconds=210,
        genre="Rock",
        year=2024,
        external_links={"spotify": "https://spotify.com/song1"}
    )
    song2 = Song(
        title="Integration Song 2",
        album_id=album.id,
        duration_seconds=180,
        genre="Rock",
        year=2024
    )
    db_session.add(song1)
    db_session.add(song2)
    await db_session.commit()
    await db_session.refresh(song1)
    await db_session.refresh(song2)

    assert song1.id is not None, "Song 1 should have ID after commit"
    assert song2.id is not None, "Song 2 should have ID after commit"
    assert song1.album_id == album.id, "Song 1 should reference correct album"
    assert song2.album_id == album.id, "Song 2 should reference correct album"

    # Step 4: Verify relationships work
    result = await db_session.execute(
        select(Artist).where(Artist.id == artist.id)
    )
    loaded_artist = result.scalar_one()

    result = await db_session.execute(
        select(Album).where(Album.artist_id == loaded_artist.id)
    )
    artist_albums = result.scalars().all()

    assert len(artist_albums) == 1, "Artist should have 1 album"

    result = await db_session.execute(
        select(Song).where(Song.album_id == album.id)
    )
    album_songs = result.scalars().all()

    assert len(album_songs) == 2, "Album should have 2 songs"


@pytest.mark.asyncio
async def test_soft_delete_restore_workflow(db_session: AsyncSession):
    """
    Test soft delete and restore workflow for songs

    Requirements:
    - 13.2: Create song → soft delete → verify 404 → restore → verify 200
    - 11.1, 11.2, 11.3: Soft delete functionality
    """
    # Create artist and album
    artist = Artist(name="Soft Delete Artist", country="BR")
    db_session.add(artist)
    await db_session.commit()
    await db_session.refresh(artist)

    album = Album(
        title="Soft Delete Album",
        artist_id=artist.id,
        release_year=2023
    )
    db_session.add(album)
    await db_session.commit()
    await db_session.refresh(album)

    # Create song
    song = Song(
        title="Soft Delete Song",
        album_id=album.id,
        duration_seconds=200
    )
    db_session.add(song)
    await db_session.commit()
    await db_session.refresh(song)

    song_id = song.id

    # Verify song is active (not deleted)
    result = await db_session.execute(
        select(Song).where(Song.id == song_id, Song.deleted_at.is_(None))
    )
    active_song = result.scalar_one_or_none()
    assert active_song is not None, "Song should be active initially"
    assert active_song.deleted_at is None, "Song should not have deleted_at timestamp"

    # Soft delete song
    song.deleted_at = datetime.utcnow()
    await db_session.commit()

    # Verify song is soft deleted (not in active query)
    result = await db_session.execute(
        select(Song).where(Song.id == song_id, Song.deleted_at.is_(None))
    )
    active_song = result.scalar_one_or_none()
    assert active_song is None, "Song should not appear in active query after soft delete"

    # Verify song exists with include_deleted
    result = await db_session.execute(
        select(Song).where(Song.id == song_id)
    )
    deleted_song = result.scalar_one_or_none()
    assert deleted_song is not None, "Song should still exist in database"
    assert deleted_song.deleted_at is not None, "Song should have deleted_at timestamp"

    # Restore song
    deleted_song.deleted_at = None
    await db_session.commit()

    # Verify song is restored
    result = await db_session.execute(
        select(Song).where(Song.id == song_id, Song.deleted_at.is_(None))
    )
    restored_song = result.scalar_one_or_none()
    assert restored_song is not None, "Song should be restored"
    assert restored_song.deleted_at is None, "Song should not have deleted_at after restore"


@pytest.mark.asyncio
async def test_pagination_consistency_artist_album_song(db_session: AsyncSession):
    """
    Test pagination consistency across all entities

    Requirements:
    - 13.3: Create 50 artists, 50 albums, 50 songs
    - Verify pagination works correctly across all entities
    - 2.2: Default page size 20, max 100
    """
    # Create 50 artists
    artists = []
    for i in range(50):
        artist = Artist(name=f"Pagination Artist {i:02d}", country="US")
        artists.append(artist)
        db_session.add(artist)
    await db_session.commit()

    # Refresh to get IDs
    for artist in artists:
        await db_session.refresh(artist)

    # Create 50 albums (distributed across artists)
    albums = []
    for i in range(50):
        album = Album(
            title=f"Pagination Album {i:02d}",
            artist_id=artists[i % 50].id,
            release_year=2020 + (i % 5)
        )
        albums.append(album)
        db_session.add(album)
    await db_session.commit()

    for album in albums:
        await db_session.refresh(album)

    # Create 50 songs (distributed across albums)
    songs = []
    for i in range(50):
        song = Song(
            title=f"Pagination Song {i:02d}",
            album_id=albums[i % 50].id,
            duration_seconds=180 + i
        )
        songs.append(song)
        db_session.add(song)
    await db_session.commit()

    # Test artist pagination
    result = await db_session.execute(
        select(Artist).order_by(Artist.name).limit(20).offset(0)
    )
    page1_artists = result.scalars().all()
    assert len(page1_artists) == 20, "First page should have 20 artists"

    result = await db_session.execute(
        select(Artist).order_by(Artist.name).limit(20).offset(20)
    )
    page2_artists = result.scalars().all()
    assert len(page2_artists) == 20, "Second page should have 20 artists"

    result = await db_session.execute(
        select(Artist).order_by(Artist.name).limit(20).offset(40)
    )
    page3_artists = result.scalars().all()
    assert len(page3_artists) >= 10, "Third page should have at least 10 artists"

    # Verify no duplicates between pages
    page1_ids = {a.id for a in page1_artists}
    page2_ids = {a.id for a in page2_artists}
    assert len(page1_ids & page2_ids) == 0, "Pages should not have duplicate artists"

    # Test album pagination
    result = await db_session.execute(
        select(Album).order_by(Album.release_year.desc()).limit(20)
    )
    album_page1 = result.scalars().all()
    assert len(album_page1) == 20, "Album pagination should return 20 items"

    # Test song pagination
    result = await db_session.execute(
        select(Song).where(Song.deleted_at.is_(None)).order_by(Song.title).limit(20)
    )
    song_page1 = result.scalars().all()
    assert len(song_page1) == 20, "Song pagination should return 20 items"

    # Test total count
    result = await db_session.execute(select(func.count()).select_from(Artist))
    total_artists = result.scalar()
    assert total_artists >= 50, "Should have at least 50 artists"

    result = await db_session.execute(select(func.count()).select_from(Album))
    total_albums = result.scalar()
    assert total_albums >= 50, "Should have at least 50 albums"

    result = await db_session.execute(select(func.count()).select_from(Song))
    total_songs = result.scalar()
    assert total_songs >= 50, "Should have at least 50 songs"


@pytest.mark.asyncio
async def test_search_artists_case_insensitive(db_session: AsyncSession):
    """
    Test artist search is case-insensitive and partial match

    Requirements:
    - 13.4: Search functionality across entities
    - 3.3: Trigram index search
    """
    # Create test artists with different cases
    artists = [
        Artist(name="Rock Legend", country="US"),
        Artist(name="ROCK STAR", country="GB"),
        Artist(name="The Rock Band", country="CA"),
        Artist(name="Jazz Musician", country="FR"),
        Artist(name="Classical Composer", country="DE")
    ]
    for artist in artists:
        db_session.add(artist)
    await db_session.commit()

    # Case-insensitive search for "rock"
    result = await db_session.execute(
        select(Artist).where(Artist.name.ilike("%rock%"))
    )
    rock_artists = result.scalars().all()

    assert len(rock_artists) == 3, "Should find 3 artists matching 'rock' (case-insensitive)"

    rock_names = [a.name for a in rock_artists]
    assert "Rock Legend" in rock_names, "Should find 'Rock Legend'"
    assert "ROCK STAR" in rock_names, "Should find 'ROCK STAR'"
    assert "The Rock Band" in rock_names, "Should find 'The Rock Band'"


@pytest.mark.asyncio
async def test_search_returns_empty_for_no_match(db_session: AsyncSession):
    """
    Test search returns empty results when no match found

    Requirements:
    - 13.4: Search should handle no matches gracefully
    """
    # Create artists
    artists = [
        Artist(name="Artist One", country="US"),
        Artist(name="Artist Two", country="GB")
    ]
    for artist in artists:
        db_session.add(artist)
    await db_session.commit()

    # Search for non-existent term
    result = await db_session.execute(
        select(Artist).where(Artist.name.ilike("%nonexistent%"))
    )
    no_match_artists = result.scalars().all()

    assert len(no_match_artists) == 0, "Should return empty list for no match"


@pytest.mark.asyncio
async def test_soft_delete_excludes_from_list_queries(db_session: AsyncSession):
    """
    Test that soft-deleted songs are excluded from default list queries

    Requirements:
    - 11.3: Exclude deleted songs from queries
    - 13.2: Verify soft delete filtering
    """
    # Create artist and album
    artist = Artist(name="List Test Artist", country="JP")
    db_session.add(artist)
    await db_session.commit()
    await db_session.refresh(artist)

    album = Album(
        title="List Test Album",
        artist_id=artist.id,
        release_year=2022
    )
    db_session.add(album)
    await db_session.commit()
    await db_session.refresh(album)

    # Create 5 active songs and 3 deleted songs
    for i in range(5):
        song = Song(
            title=f"Active Song {i}",
            album_id=album.id,
            duration_seconds=180
        )
        db_session.add(song)

    for i in range(3):
        song = Song(
            title=f"Deleted Song {i}",
            album_id=album.id,
            duration_seconds=180,
            deleted_at=datetime.utcnow()
        )
        db_session.add(song)

    await db_session.commit()

    # Query without deleted filter (should exclude deleted)
    result = await db_session.execute(
        select(Song).where(
            Song.album_id == album.id,
            Song.deleted_at.is_(None)
        )
    )
    active_songs = result.scalars().all()
    assert len(active_songs) == 5, "Should only return active songs"

    # Query with deleted included
    result = await db_session.execute(
        select(Song).where(Song.album_id == album.id)
    )
    all_songs = result.scalars().all()
    assert len(all_songs) == 8, "Should return all songs when including deleted"


@pytest.mark.asyncio
async def test_album_filtering_by_artist(db_session: AsyncSession):
    """
    Test album filtering by artist_id

    Requirements:
    - 13.3: Filtering functionality
    - 6.2: Filter albums by artist
    """
    # Create artists
    artist1 = Artist(name="Filter Artist 1", country="US")
    artist2 = Artist(name="Filter Artist 2", country="CA")
    db_session.add(artist1)
    db_session.add(artist2)
    await db_session.commit()
    await db_session.refresh(artist1)
    await db_session.refresh(artist2)

    # Create albums for artist1
    for i in range(3):
        album = Album(
            title=f"Artist 1 Album {i}",
            artist_id=artist1.id,
            release_year=2020 + i
        )
        db_session.add(album)

    # Create albums for artist2
    for i in range(2):
        album = Album(
            title=f"Artist 2 Album {i}",
            artist_id=artist2.id,
            release_year=2021 + i
        )
        db_session.add(album)

    await db_session.commit()

    # Filter by artist1
    result = await db_session.execute(
        select(Album).where(Album.artist_id == artist1.id)
    )
    artist1_albums = result.scalars().all()
    assert len(artist1_albums) == 3, "Should find 3 albums for artist1"

    # Filter by artist2
    result = await db_session.execute(
        select(Album).where(Album.artist_id == artist2.id)
    )
    artist2_albums = result.scalars().all()
    assert len(artist2_albums) == 2, "Should find 2 albums for artist2"


@pytest.mark.asyncio
async def test_song_filtering_by_album(db_session: AsyncSession):
    """
    Test song filtering by album_id

    Requirements:
    - 13.3: Filtering functionality
    - 9.2: Filter songs by album
    """
    # Create artist
    artist = Artist(name="Song Filter Artist", country="BR")
    db_session.add(artist)
    await db_session.commit()
    await db_session.refresh(artist)

    # Create albums
    album1 = Album(
        title="Song Filter Album 1",
        artist_id=artist.id,
        release_year=2020
    )
    album2 = Album(
        title="Song Filter Album 2",
        artist_id=artist.id,
        release_year=2021
    )
    db_session.add(album1)
    db_session.add(album2)
    await db_session.commit()
    await db_session.refresh(album1)
    await db_session.refresh(album2)

    # Create songs for album1
    for i in range(4):
        song = Song(
            title=f"Album 1 Song {i}",
            album_id=album1.id,
            duration_seconds=180 + i
        )
        db_session.add(song)

    # Create songs for album2
    for i in range(3):
        song = Song(
            title=f"Album 2 Song {i}",
            album_id=album2.id,
            duration_seconds=200 + i
        )
        db_session.add(song)

    await db_session.commit()

    # Filter by album1
    result = await db_session.execute(
        select(Song).where(
            Song.album_id == album1.id,
            Song.deleted_at.is_(None)
        )
    )
    album1_songs = result.scalars().all()
    assert len(album1_songs) == 4, "Should find 4 songs for album1"

    # Filter by album2
    result = await db_session.execute(
        select(Song).where(
            Song.album_id == album2.id,
            Song.deleted_at.is_(None)
        )
    )
    album2_songs = result.scalars().all()
    assert len(album2_songs) == 3, "Should find 3 songs for album2"
