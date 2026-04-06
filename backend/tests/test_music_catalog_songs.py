"""
Test Database Schema for Songs - Task 1.3
Test-Driven Development (TDD): RED phase

Tests for songs table schema with album relationship and soft delete
Requirements: 8.1, 8.2, 8.3, 8.4, 11.1, 11.2, 12.1, 12.4, 12.6, 13.4
"""
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_songs_table_exists(db_session: AsyncSession):
    """
    Test that songs table exists with correct columns

    Requirements:
    - 8.1: Song creation
    - 11.1: Soft delete pattern
    """
    result = await db_session.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = 'songs'
        );
    """))
    table_exists = result.scalar()

    assert table_exists is True, "Songs table should exist"


@pytest.mark.asyncio
async def test_songs_table_columns(db_session: AsyncSession):
    """
    Test songs table has required columns with correct types

    Requirements:
    - 8.1: Song creation
    - 8.2: Validate title length (1-200 characters)
    - 8.4: Validate duration (1-7200 seconds)
    - 11.1: deleted_at for soft delete
    """
    result = await db_session.execute(text("""
        SELECT column_name, data_type, character_maximum_length, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'songs'
        ORDER BY ordinal_position;
    """))
    columns = {row[0]: {"type": row[1], "max_length": row[2], "nullable": row[3]}
               for row in result.fetchall()}

    # Verify required columns exist
    assert "id" in columns, "Songs table should have id column"
    assert "title" in columns, "Songs table should have title column"
    assert "album_id" in columns, "Songs table should have album_id column"
    assert "duration_seconds" in columns, "Songs table should have duration_seconds column"
    assert "genre" in columns, "Songs table should have genre column"
    assert "year" in columns, "Songs table should have year column"
    assert "external_links" in columns, "Songs table should have external_links column"
    assert "deleted_at" in columns, "Songs table should have deleted_at column"
    assert "created_at" in columns, "Songs table should have created_at column"
    assert "updated_at" in columns, "Songs table should have updated_at column"

    # Verify column types
    assert columns["title"]["type"] == "character varying", "title should be VARCHAR"
    assert columns["title"]["max_length"] == 200, "title should be max 200 characters"
    assert columns["album_id"]["type"] == "integer", "album_id should be INTEGER"
    assert columns["duration_seconds"]["type"] == "integer", "duration_seconds should be INTEGER"
    assert columns["external_links"]["type"] == "jsonb", "external_links should be JSONB"
    assert columns["deleted_at"]["type"] == "timestamp with time zone", "deleted_at should be TIMESTAMPTZ"
    assert columns["title"]["nullable"] == "NO", "title should be NOT NULL"
    assert columns["album_id"]["nullable"] == "NO", "album_id should be NOT NULL"
    assert columns["deleted_at"]["nullable"] == "YES", "deleted_at should be nullable"


@pytest.mark.asyncio
async def test_songs_foreign_key_to_albums(db_session: AsyncSession):
    """
    Test that foreign key constraint exists from songs to albums with ON DELETE CASCADE

    Requirements:
    - 12.1: ON DELETE CASCADE for album → songs
    - 12.6: NOT NULL constraint on album_id
    """
    result = await db_session.execute(text("""
        SELECT
            tc.constraint_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name,
            rc.delete_rule
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
          ON ccu.constraint_name = tc.constraint_name
        JOIN information_schema.referential_constraints AS rc
          ON rc.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_name = 'songs'
          AND kcu.column_name = 'album_id';
    """))
    fk_constraint = result.fetchone()

    assert fk_constraint is not None, "Foreign key constraint should exist on album_id"
    assert fk_constraint[2] == "albums", "Foreign key should reference albums table"
    assert fk_constraint[3] == "id", "Foreign key should reference id column"
    assert fk_constraint[4] == "CASCADE", "Foreign key should have ON DELETE CASCADE"


@pytest.mark.asyncio
async def test_songs_duration_check_constraint(db_session: AsyncSession):
    """
    Test that CHECK constraint exists on duration_seconds (1-7200)

    Requirements:
    - 8.4: Validate duration between 1 and 7200 seconds
    """
    result = await db_session.execute(text("""
        SELECT constraint_name, check_clause
        FROM information_schema.check_constraints
        WHERE constraint_name LIKE '%duration%'
          AND constraint_schema = 'public';
    """))
    check_constraint = result.fetchone()

    assert check_constraint is not None, "CHECK constraint should exist on duration_seconds"
    # Verify it checks between 1 and 7200
    check_clause = check_constraint[1].lower()
    assert "duration_seconds" in check_clause, "CHECK should reference duration_seconds"
    assert "1" in check_clause and "7200" in check_clause, "CHECK should enforce 1-7200 range"


@pytest.mark.asyncio
async def test_songs_album_id_index(db_session: AsyncSession):
    """
    Test that index exists on album_id for FK lookup

    Requirements:
    - 13.4: Implement indexes for performance
    """
    result = await db_session.execute(text("""
        SELECT indexname
        FROM pg_indexes
        WHERE tablename = 'songs' AND indexdef LIKE '%album_id%';
    """))
    indexes = result.fetchall()

    assert len(indexes) > 0, "Songs table should have index on album_id"


@pytest.mark.asyncio
async def test_songs_deleted_at_index(db_session: AsyncSession):
    """
    Test that index exists on deleted_at for soft delete filtering

    Requirements:
    - 11.3: Exclude deleted songs from queries
    - 13.4: Implement indexes for performance
    """
    result = await db_session.execute(text("""
        SELECT indexname
        FROM pg_indexes
        WHERE tablename = 'songs' AND indexdef LIKE '%deleted_at%';
    """))
    indexes = result.fetchall()

    assert len(indexes) > 0, "Songs table should have index on deleted_at"


@pytest.mark.asyncio
async def test_songs_active_partial_index(db_session: AsyncSession):
    """
    Test that partial index exists on id WHERE deleted_at IS NULL for active songs

    Requirements:
    - 11.3: Exclude deleted songs from queries
    - 13.4: Optimize performance for active songs
    """
    result = await db_session.execute(text("""
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE tablename = 'songs' AND indexdef LIKE '%WHERE%deleted_at IS NULL%';
    """))
    indexes = result.fetchall()

    assert len(indexes) > 0, "Songs table should have partial index for active songs (deleted_at IS NULL)"


@pytest.mark.asyncio
async def test_songs_title_trigram_index(db_session: AsyncSession):
    """
    Test that trigram GIN index exists on title column for search

    Requirements:
    - 13.4: Search performance
    """
    result = await db_session.execute(text("""
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE tablename = 'songs' AND indexdef LIKE '%gin%title%';
    """))
    indexes = result.fetchall()

    assert len(indexes) > 0, "Songs table should have trigram GIN index on title"
    assert any("gin_trgm_ops" in idx[1] for idx in indexes), \
        "GIN index should use gin_trgm_ops for trigram search"


@pytest.mark.asyncio
async def test_songs_genre_index(db_session: AsyncSession):
    """
    Test that index exists on genre for filtering

    Requirements:
    - 13.4: Implement indexes for filtering
    """
    result = await db_session.execute(text("""
        SELECT indexname
        FROM pg_indexes
        WHERE tablename = 'songs' AND indexdef LIKE '%genre%';
    """))
    indexes = result.fetchall()

    assert len(indexes) > 0, "Songs table should have index on genre"


@pytest.mark.asyncio
async def test_songs_updated_at_trigger(db_session: AsyncSession):
    """
    Test that trigger exists to automatically update updated_at timestamp

    Requirements:
    - 8.5: Set timestamps automatically
    """
    result = await db_session.execute(text("""
        SELECT trigger_name, event_manipulation
        FROM information_schema.triggers
        WHERE event_object_table = 'songs' AND trigger_name LIKE '%updated_at%';
    """))
    triggers = result.fetchall()

    assert len(triggers) > 0, "Songs table should have trigger for updated_at"
    trigger = triggers[0]
    assert trigger[1] == "UPDATE", "Trigger should fire on UPDATE"
