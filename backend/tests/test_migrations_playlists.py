"""
Test migrations for playlists tables - Task 1.1, 1.2
Requirements: 1, 8, 5, 12
"""
import pytest
import asyncio
from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.database import DATABASE_URL


@pytest.mark.asyncio
async def test_playlists_table_exists(db_session: AsyncSession):
    """
    RED phase - Test playlists table structure
    Task 1.1: Create database migration for playlists table
    """
    result = await db_session.execute(
        text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'playlists'
            ORDER BY ordinal_position
        """)
    )
    columns = result.fetchall()

    # Should have 6 columns: id, title, owner_user_id, is_public, created_at, updated_at
    assert len(columns) == 6, f"Expected 6 columns, got {len(columns)}"

    column_dict = {col[0]: col for col in columns}

    # Verify id column
    assert 'id' in column_dict
    assert column_dict['id'][1] == 'integer'
    assert column_dict['id'][2] == 'NO'  # NOT NULL

    # Verify title column
    assert 'title' in column_dict
    assert 'character varying' in column_dict['title'][1]
    assert column_dict['title'][2] == 'NO'  # NOT NULL

    # Verify owner_user_id column
    assert 'owner_user_id' in column_dict
    assert column_dict['owner_user_id'][1] == 'integer'
    assert column_dict['owner_user_id'][2] == 'NO'  # NOT NULL

    # Verify is_public column
    assert 'is_public' in column_dict
    assert column_dict['is_public'][1] == 'boolean'
    assert column_dict['is_public'][2] == 'NO'  # NOT NULL
    assert 'false' in column_dict['is_public'][3].lower()  # DEFAULT FALSE

    # Verify timestamps
    assert 'created_at' in column_dict
    assert 'timestamp' in column_dict['created_at'][1]
    assert 'updated_at' in column_dict
    assert 'timestamp' in column_dict['updated_at'][1]


@pytest.mark.asyncio
async def test_playlists_table_indexes(db_session: AsyncSession):
    """
    RED phase - Test playlists table indexes
    Task 1.1: Verify indexes on owner_user_id and is_public
    """
    result = await db_session.execute(
        text("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'playlists'
        """)
    )
    indexes = result.fetchall()

    index_names = [idx[0] for idx in indexes]

    # Should have primary key index
    assert any('pkey' in name for name in index_names), "Missing primary key index"

    # Should have index on owner_user_id
    assert any('owner' in name.lower() for name in index_names), "Missing index on owner_user_id"

    # Should have partial index on is_public
    public_indexes = [idx for idx in indexes if 'public' in idx[0].lower()]
    assert len(public_indexes) > 0, "Missing index on is_public"
    # Verify it's a partial index (WHERE clause)
    assert any('WHERE' in idx[1] for idx in public_indexes), "is_public index should be partial"


@pytest.mark.asyncio
async def test_playlists_table_foreign_key(db_session: AsyncSession):
    """
    RED phase - Test playlists foreign key to users
    Task 1.1: Verify foreign key constraint on owner_user_id
    """
    result = await db_session.execute(
        text("""
            SELECT
                tc.constraint_name,
                tc.constraint_type,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name,
                rc.delete_rule
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            LEFT JOIN information_schema.referential_constraints AS rc
                ON tc.constraint_name = rc.constraint_name
            WHERE tc.table_name = 'playlists' AND tc.constraint_type = 'FOREIGN KEY'
        """)
    )
    foreign_keys = result.fetchall()

    assert len(foreign_keys) == 1, f"Expected 1 foreign key, got {len(foreign_keys)}"

    fk = foreign_keys[0]
    assert fk[2] == 'owner_user_id', "Foreign key should be on owner_user_id"
    assert fk[3] == 'users', "Foreign key should reference users table"
    assert fk[4] == 'id', "Foreign key should reference users.id"
    assert fk[5] == 'CASCADE', "Foreign key should have ON DELETE CASCADE"


@pytest.mark.asyncio
async def test_playlist_songs_table_exists(db_session: AsyncSession):
    """
    RED phase - Test playlist_songs join table structure
    Task 1.2: Create database migration for playlist_songs table
    """
    result = await db_session.execute(
        text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'playlist_songs'
            ORDER BY ordinal_position
        """)
    )
    columns = result.fetchall()

    # Should have 5 columns: id, playlist_id, song_id, position, created_at
    assert len(columns) == 5, f"Expected 5 columns, got {len(columns)}"

    column_dict = {col[0]: col for col in columns}

    # Verify surrogate key (allows duplicates)
    assert 'id' in column_dict
    assert column_dict['id'][1] == 'integer'
    assert column_dict['id'][2] == 'NO'  # NOT NULL

    # Verify playlist_id
    assert 'playlist_id' in column_dict
    assert column_dict['playlist_id'][1] == 'integer'
    assert column_dict['playlist_id'][2] == 'NO'

    # Verify song_id
    assert 'song_id' in column_dict
    assert column_dict['song_id'][1] == 'integer'
    assert column_dict['song_id'][2] == 'NO'

    # Verify position
    assert 'position' in column_dict
    assert column_dict['position'][1] == 'integer'
    assert column_dict['position'][2] == 'NO'

    # Verify created_at
    assert 'created_at' in column_dict
    assert 'timestamp' in column_dict['created_at'][1]


@pytest.mark.asyncio
async def test_playlist_songs_foreign_keys(db_session: AsyncSession):
    """
    RED phase - Test playlist_songs foreign keys
    Task 1.2: Verify CASCADE and RESTRICT constraints
    """
    result = await db_session.execute(
        text("""
            SELECT
                tc.constraint_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                rc.delete_rule
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            JOIN information_schema.referential_constraints AS rc
                ON tc.constraint_name = rc.constraint_name
            WHERE tc.table_name = 'playlist_songs' AND tc.constraint_type = 'FOREIGN KEY'
            ORDER BY kcu.column_name
        """)
    )
    foreign_keys = result.fetchall()

    assert len(foreign_keys) == 2, f"Expected 2 foreign keys, got {len(foreign_keys)}"

    # Find playlist_id FK
    playlist_fk = [fk for fk in foreign_keys if fk[1] == 'playlist_id'][0]
    assert playlist_fk[2] == 'playlists', "playlist_id should reference playlists table"
    assert playlist_fk[3] == 'CASCADE', "playlist_id FK should have ON DELETE CASCADE"

    # Find song_id FK
    song_fk = [fk for fk in foreign_keys if fk[1] == 'song_id'][0]
    assert song_fk[2] == 'songs', "song_id should reference songs table"
    assert song_fk[3] == 'RESTRICT', "song_id FK should have ON DELETE RESTRICT"


@pytest.mark.asyncio
async def test_playlist_songs_indexes(db_session: AsyncSession):
    """
    RED phase - Test playlist_songs composite index
    Task 1.2: Verify composite index on (playlist_id, position)
    """
    result = await db_session.execute(
        text("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'playlist_songs'
        """)
    )
    indexes = result.fetchall()

    index_defs = [idx[1] for idx in indexes]

    # Should have composite index on (playlist_id, position)
    composite_indexes = [idx for idx in index_defs if 'playlist_id' in idx and 'position' in idx]
    assert len(composite_indexes) > 0, "Missing composite index on (playlist_id, position)"

    # Should have index on song_id for reverse lookups
    song_indexes = [idx for idx in index_defs if 'song_id' in idx and 'playlist_id' not in idx]
    assert len(song_indexes) > 0, "Missing index on song_id"


@pytest.mark.asyncio
async def test_playlist_songs_no_unique_constraint(db_session: AsyncSession):
    """
    RED phase - Verify NO unique constraint on (playlist_id, song_id)
    Task 1.2: Allow duplicate songs
    Requirement: 12 (Duplicate Song Handling)
    """
    result = await db_session.execute(
        text("""
            SELECT constraint_name, constraint_type
            FROM information_schema.table_constraints
            WHERE table_name = 'playlist_songs'
                AND constraint_type = 'UNIQUE'
                AND constraint_name NOT LIKE '%pkey'
        """)
    )
    unique_constraints = result.fetchall()

    # Should have NO unique constraint (except primary key)
    assert len(unique_constraints) == 0, "Should not have unique constraint to allow duplicate songs"
