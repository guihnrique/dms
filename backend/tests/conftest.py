"""
Pytest configuration and fixtures for tests
Provides database setup, async client, and test cleanup
"""
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.main import app
from app.database import get_db, Base
from app.models import user, auth_audit_log  # Import to register models

# Test database URL (use same as development for now)
# Load from environment variable
import os
from dotenv import load_dotenv

load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", os.getenv("DATABASE_URL"))

# Create test engine with SSL
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"ssl": "require"}
)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database session for each test

    Yields:
        AsyncSession: Database session
    """
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create async HTTP client for testing with database override

    Args:
        db_session: Database session fixture

    Yields:
        AsyncClient: HTTP client for testing
    """
    async def override_get_db():
        try:
            yield db_session
            await db_session.commit()
        except Exception:
            await db_session.rollback()
            raise

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()

    # Ensure session is properly closed
    await db_session.rollback()


# NOTE: No cleanup fixture - using unique emails per test for isolation


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user for playlist ownership tests"""
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


@pytest_asyncio.fixture
async def test_playlist(db_session: AsyncSession, test_user):
    """Create a test playlist"""
    from app.models.playlist import Playlist

    playlist = Playlist(
        title="Test Playlist",
        owner_user_id=test_user.id,
        is_public=False
    )

    db_session.add(playlist)
    await db_session.commit()
    await db_session.refresh(playlist)

    return playlist


@pytest_asyncio.fixture
async def test_song(db_session: AsyncSession):
    """Create a test song for playlist tests"""
    from app.models.song import Song
    from app.models.album import Album
    from app.models.artist import Artist

    # Create artist
    artist = Artist(name="Test Artist", country="US")
    db_session.add(artist)
    await db_session.flush()

    # Create album
    album = Album(
        title="Test Album",
        artist_id=artist.id,
        release_year=2024
    )
    db_session.add(album)
    await db_session.flush()

    # Create song
    song = Song(
        title="Test Song",
        album_id=album.id,
        duration_seconds=180
    )
    db_session.add(song)
    await db_session.commit()
    await db_session.refresh(song)

    return song
