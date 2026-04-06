"""
Test Database Schema for Music Catalog - Task 1.1
Test-Driven Development (TDD): RED phase

Tests for artists table schema with trigram GIN indexes
Requirements: 1.1, 1.2, 1.3, 1.4, 3.4, 13.4
"""
import pytest
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_artists_table_exists(db_session: AsyncSession):
    """
    Test that artists table exists with correct columns

    Requirements:
    - 1.1: Artist creation with validation
    - 1.4: Set timestamps automatically
    """
    # Query table existence
    result = await db_session.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = 'artists'
        );
    """))
    table_exists = result.scalar()

    assert table_exists is True, "Artists table should exist"


@pytest.mark.asyncio
async def test_artists_table_columns(db_session: AsyncSession):
    """
    Test artists table has required columns with correct types

    Requirements:
    - 1.1: Artist record creation
    - 1.2: Validate name length (1-200 characters)
    - 1.3: Validate country code (ISO 3166-1 alpha-2)
    """
    # Query column definitions
    result = await db_session.execute(text("""
        SELECT column_name, data_type, character_maximum_length, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'artists'
        ORDER BY ordinal_position;
    """))
    columns = {row[0]: {"type": row[1], "max_length": row[2], "nullable": row[3]}
               for row in result.fetchall()}

    # Verify required columns exist
    assert "id" in columns, "Artists table should have id column"
    assert "name" in columns, "Artists table should have name column"
    assert "country" in columns, "Artists table should have country column"
    assert "created_at" in columns, "Artists table should have created_at column"
    assert "updated_at" in columns, "Artists table should have updated_at column"

    # Verify column types
    assert columns["name"]["type"] == "character varying", "name should be VARCHAR"
    assert columns["name"]["max_length"] == 200, "name should be max 200 characters"
    assert columns["country"]["max_length"] == 2, "country should be 2 characters (ISO alpha-2)"
    assert columns["name"]["nullable"] == "NO", "name should be NOT NULL"
    assert columns["country"]["nullable"] == "NO", "country should be NOT NULL"


@pytest.mark.asyncio
async def test_artists_trigram_index_exists(db_session: AsyncSession):
    """
    Test that trigram GIN index exists on name column for fast search

    Requirements:
    - 3.4: Search performance (<200ms for 10k artists)
    - 13.4: Implement indexes for performance
    """
    # Query for GIN index on name column
    result = await db_session.execute(text("""
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE tablename = 'artists' AND indexdef LIKE '%gin%name%';
    """))
    indexes = result.fetchall()

    assert len(indexes) > 0, "Artists table should have trigram GIN index on name column"
    # Verify it uses gin_trgm_ops (trigram operator class)
    assert any("gin_trgm_ops" in idx[1] for idx in indexes), \
        "GIN index should use gin_trgm_ops for trigram search"


@pytest.mark.asyncio
async def test_artists_country_index_exists(db_session: AsyncSession):
    """
    Test that standard index exists on country column for filtering

    Requirements:
    - 13.4: Implement indexes for performance
    """
    # Query for index on country column
    result = await db_session.execute(text("""
        SELECT indexname
        FROM pg_indexes
        WHERE tablename = 'artists' AND indexdef LIKE '%country%'
        AND indexdef NOT LIKE '%gin%';
    """))
    indexes = result.fetchall()

    assert len(indexes) > 0, "Artists table should have index on country column"


@pytest.mark.asyncio
async def test_artists_updated_at_trigger_exists(db_session: AsyncSession):
    """
    Test that trigger exists to automatically update updated_at timestamp

    Requirements:
    - 1.4: Set created_at and updated_at timestamps
    """
    # Query for trigger
    result = await db_session.execute(text("""
        SELECT trigger_name, event_manipulation, action_statement
        FROM information_schema.triggers
        WHERE event_object_table = 'artists' AND trigger_name LIKE '%updated_at%';
    """))
    triggers = result.fetchall()

    assert len(triggers) > 0, "Artists table should have trigger for updated_at"
    trigger = triggers[0]
    assert trigger[1] == "UPDATE", "Trigger should fire on UPDATE"


@pytest.mark.asyncio
async def test_pg_trgm_extension_enabled(db_session: AsyncSession):
    """
    Test that pg_trgm extension is enabled for trigram search

    Requirements:
    - 3.4: Search performance with trigram index
    """
    result = await db_session.execute(text("""
        SELECT EXISTS (
            SELECT FROM pg_extension WHERE extname = 'pg_trgm'
        );
    """))
    extension_exists = result.scalar()

    assert extension_exists is True, "pg_trgm extension should be enabled"
