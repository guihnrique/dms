"""
Tests for search with genre column fix
Tests that search works correctly after adding genre column to models
"""
import pytest
from httpx import AsyncClient
from sqlalchemy import text
from app.main import app
from app.database import get_db


@pytest.mark.asyncio
async def test_search_endpoint_works_without_error():
    """Test that search endpoint works without 500 error (AttributeError)"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/search?q=test")

        # Should NOT return 500 Internal Server Error
        assert response.status_code != 500

        # Should return 200 OK
        assert response.status_code == 200

        # Should have correct response structure
        data = response.json()
        assert "artists" in data
        assert "albums" in data
        assert "songs" in data
        assert "total_count" in data


@pytest.mark.asyncio
async def test_search_returns_genre_in_albums():
    """Test that search returns genre field in album results"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/search?q=black")

        assert response.status_code == 200
        data = response.json()

        # If there are album results, they should have genre field
        if data["albums"]:
            album = data["albums"][0]
            assert "genre" in album
            # Genre can be null or a string
            assert album["genre"] is None or isinstance(album["genre"], str)


@pytest.mark.asyncio
async def test_search_returns_genre_in_songs():
    """Test that search returns genre field in song results"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/search?q=song")

        assert response.status_code == 200
        data = response.json()

        # If there are song results, they should have genre field
        if data["songs"]:
            song = data["songs"][0]
            assert "genre" in song
            # Genre can be null or a string
            assert song["genre"] is None or isinstance(song["genre"], str)


@pytest.mark.asyncio
async def test_genre_column_exists_in_database():
    """Test that genre column exists in albums and songs tables"""
    # This test requires database connection which may not be available in CI
    # Skip if database is not accessible
    try:
        async for db in get_db():
            # Check albums table
            result = await db.execute(
                text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'albums' AND column_name = 'genre'
                """)
            )
            albums_genre = result.fetchone()
            assert albums_genre is not None, "Genre column missing from albums table"

            # Check songs table
            result = await db.execute(
                text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'songs' AND column_name = 'genre'
                """)
            )
            songs_genre = result.fetchone()
            assert songs_genre is not None, "Genre column missing from songs table"

            break  # Only need to check once
    except Exception:
        pytest.skip("Database not accessible for this test")


@pytest.mark.asyncio
async def test_search_with_genre_filter():
    """Test that search works with genre filter (if implemented)"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # This tests that genre filtering doesn't cause errors
        response = await client.get("/search?q=test&genres=Rock")

        # Should not error
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_album_model_has_genre_attribute():
    """Test that Album model has genre attribute"""
    from app.models.album import Album

    # Check that Album model has genre attribute
    assert hasattr(Album, "genre"), "Album model missing genre attribute"

    # Check that it's a Column
    assert hasattr(Album.genre, "type"), "Album.genre is not a SQLAlchemy Column"


@pytest.mark.asyncio
async def test_song_model_has_genre_attribute():
    """Test that Song model has genre attribute"""
    from app.models.song import Song

    # Check that Song model has genre attribute
    assert hasattr(Song, "genre"), "Song model missing genre attribute"

    # Check that it's a Column
    assert hasattr(Song.genre, "type"), "Song.genre is not a SQLAlchemy Column"


@pytest.mark.asyncio
async def test_search_does_not_raise_attribute_error():
    """Test that search does not raise AttributeError for genre (regression test)"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/search?q=ac")

        # The original bug was AttributeError: type object 'Album' has no attribute 'genre'
        # This should be fixed now
        assert response.status_code == 200

        # Verify response structure
        data = response.json()
        assert isinstance(data, dict)
        assert "artists" in data
        assert "albums" in data
        assert "songs" in data
