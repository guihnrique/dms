"""
Test Database Schema for Albums - Task 1.2
Test-Driven Development (TDD): RED phase

Tests for albums table schema with artist relationship
Requirements: 5.1, 5.2, 5.3, 6.2, 12.2, 12.6, 13.4
"""
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_albums_table_exists(db_session: AsyncSession):
    """
    Test that albums table exists with correct columns

    Requirements:
    - 5.1: Album creation
    - 6.2: Album ordering by release_year
    """
    result = await db_session.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = 'albums'
        );
    """))
    table_exists = result.scalar()

    assert table_exists is True, "Albums table should exist"


@pytest.mark.asyncio
async def test_albums_table_columns(db_session: AsyncSession):
    """
    Test albums table has required columns with correct types

    Requirements:
    - 5.1: Album creation
    - 5.2: Validate title length (1-200 characters)
    - 5.3: Validate artist_id exists
    """
    result = await db_session.execute(text("""
        SELECT column_name, data_type, character_maximum_length, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'albums'
        ORDER BY ordinal_position;
    """))
    columns = {row[0]: {"type": row[1], "max_length": row[2], "nullable": row[3]}
               for row in result.fetchall()}

    # Verify required columns exist
    assert "id" in columns, "Albums table should have id column"
    assert "title" in columns, "Albums table should have title column"
    assert "artist_id" in columns, "Albums table should have artist_id column"
    assert "release_year" in columns, "Albums table should have release_year column"
    assert "album_cover_url" in columns, "Albums table should have album_cover_url column"
    assert "created_at" in columns, "Albums table should have created_at column"
    assert "updated_at" in columns, "Albums table should have updated_at column"

    # Verify column types
    assert columns["title"]["type"] == "character varying", "title should be VARCHAR"
    assert columns["title"]["max_length"] == 200, "title should be max 200 characters"
    assert columns["artist_id"]["type"] == "integer", "artist_id should be INTEGER"
    assert columns["release_year"]["type"] == "integer", "release_year should be INTEGER"
    assert columns["title"]["nullable"] == "NO", "title should be NOT NULL"
    assert columns["artist_id"]["nullable"] == "NO", "artist_id should be NOT NULL"
    assert columns["album_cover_url"]["nullable"] == "YES", "album_cover_url should be nullable"


@pytest.mark.asyncio
async def test_albums_foreign_key_to_artists(db_session: AsyncSession):
    """
    Test that foreign key constraint exists from albums to artists with ON DELETE RESTRICT

    Requirements:
    - 12.2: ON DELETE RESTRICT for artist → albums
    - 12.6: NOT NULL constraint on artist_id
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
          AND tc.table_name = 'albums'
          AND kcu.column_name = 'artist_id';
    """))
    fk_constraint = result.fetchone()

    assert fk_constraint is not None, "Foreign key constraint should exist on artist_id"
    assert fk_constraint[2] == "artists", "Foreign key should reference artists table"
    assert fk_constraint[3] == "id", "Foreign key should reference id column"
    assert fk_constraint[4] == "RESTRICT", "Foreign key should have ON DELETE RESTRICT"


@pytest.mark.asyncio
async def test_albums_artist_id_index(db_session: AsyncSession):
    """
    Test that index exists on artist_id for FK lookup performance

    Requirements:
    - 13.4: Implement indexes for performance
    """
    result = await db_session.execute(text("""
        SELECT indexname
        FROM pg_indexes
        WHERE tablename = 'albums' AND indexdef LIKE '%artist_id%';
    """))
    indexes = result.fetchall()

    assert len(indexes) > 0, "Albums table should have index on artist_id"


@pytest.mark.asyncio
async def test_albums_release_year_index(db_session: AsyncSession):
    """
    Test that index exists on release_year DESC for sorting

    Requirements:
    - 6.2: Order by release_year DESC, title ASC
    - 13.4: Implement indexes for performance
    """
    result = await db_session.execute(text("""
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE tablename = 'albums' AND indexdef LIKE '%release_year%';
    """))
    indexes = result.fetchall()

    assert len(indexes) > 0, "Albums table should have index on release_year"
    # Verify DESC ordering
    assert any("DESC" in idx[1] for idx in indexes), "release_year index should be DESC"


@pytest.mark.asyncio
async def test_albums_title_trigram_index(db_session: AsyncSession):
    """
    Test that trigram GIN index exists on title column for search

    Requirements:
    - 13.4: Implement indexes for search performance
    """
    result = await db_session.execute(text("""
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE tablename = 'albums' AND indexdef LIKE '%gin%title%';
    """))
    indexes = result.fetchall()

    assert len(indexes) > 0, "Albums table should have trigram GIN index on title"
    assert any("gin_trgm_ops" in idx[1] for idx in indexes), \
        "GIN index should use gin_trgm_ops for trigram search"


@pytest.mark.asyncio
async def test_albums_updated_at_trigger(db_session: AsyncSession):
    """
    Test that trigger exists to automatically update updated_at timestamp

    Requirements:
    - 5.5: Set timestamps automatically
    """
    result = await db_session.execute(text("""
        SELECT trigger_name, event_manipulation
        FROM information_schema.triggers
        WHERE event_object_table = 'albums' AND trigger_name LIKE '%updated_at%';
    """))
    triggers = result.fetchall()

    assert len(triggers) > 0, "Albums table should have trigger for updated_at"
    trigger = triggers[0]
    assert trigger[1] == "UPDATE", "Trigger should fire on UPDATE"
