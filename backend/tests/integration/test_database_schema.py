"""
Integration tests for database schema - Task 1.1
Tests verify users and auth_audit_log tables exist with correct structure
"""
import pytest
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


# Database URL for testing (will be configured via environment variable)
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test_dms"


@pytest.fixture
async def db_engine():
    """Create test database engine"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    """Create test database session"""
    async_session = sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest.mark.asyncio
async def test_users_table_exists(db_session):
    """
    RED PHASE: Test that users table exists
    Requirements: 1.1
    """
    result = await db_session.execute(
        text("SELECT to_regclass('public.users')")
    )
    table_exists = result.scalar()
    assert table_exists is not None, "users table does not exist"


@pytest.mark.asyncio
async def test_users_table_has_correct_columns(db_session):
    """
    RED PHASE: Test users table has all required columns
    Requirements: 1.1, 1.2, 1.3, 13.1
    """
    result = await db_session.execute(
        text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """)
    )
    columns = {row[0]: {"type": row[1], "nullable": row[2]} for row in result}

    # Verify all required columns exist
    required_columns = {
        "id": "integer",
        "email": "character varying",
        "password_hash": "character varying",
        "role": "character varying",
        "failed_login_attempts": "integer",
        "account_locked_until": "timestamp with time zone",
        "created_at": "timestamp with time zone",
        "updated_at": "timestamp with time zone"
    }

    for col_name, col_type in required_columns.items():
        assert col_name in columns, f"Column {col_name} missing"
        assert columns[col_name]["type"] == col_type, \
            f"Column {col_name} has wrong type: {columns[col_name]['type']}"

    # Verify NOT NULL constraints
    assert columns["email"]["nullable"] == "NO"
    assert columns["password_hash"]["nullable"] == "NO"
    assert columns["role"]["nullable"] == "NO"


@pytest.mark.asyncio
async def test_users_table_has_unique_email_index(db_session):
    """
    RED PHASE: Test unique index on email column
    Requirements: 1.1, 1.6
    """
    result = await db_session.execute(
        text("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'users' AND indexdef LIKE '%email%'
        """)
    )
    indexes = list(result)

    assert len(indexes) > 0, "No index on email column"

    # Check for UNIQUE constraint
    unique_index_found = any("UNIQUE" in idx[1] for idx in indexes)
    assert unique_index_found, "Email column does not have UNIQUE index"


@pytest.mark.asyncio
async def test_users_table_has_account_locked_partial_index(db_session):
    """
    RED PHASE: Test partial index on account_locked_until
    Requirements: 13.1
    """
    result = await db_session.execute(
        text("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'users' AND indexdef LIKE '%account_locked_until%'
        """)
    )
    indexes = list(result)

    assert len(indexes) > 0, "No index on account_locked_until column"

    # Check for partial index (WHERE clause)
    partial_index_found = any("WHERE" in idx[1] for idx in indexes)
    assert partial_index_found, "account_locked_until does not have partial index"


@pytest.mark.asyncio
async def test_users_table_has_updated_at_trigger(db_session):
    """
    RED PHASE: Test trigger for automatic updated_at timestamp
    Requirements: 1.1, 4.2, 4.3
    """
    result = await db_session.execute(
        text("""
            SELECT trigger_name
            FROM information_schema.triggers
            WHERE event_object_table = 'users'
            AND trigger_name LIKE '%updated_at%'
        """)
    )
    triggers = list(result)

    assert len(triggers) > 0, "No trigger for updated_at on users table"


@pytest.mark.asyncio
async def test_auth_audit_log_table_exists(db_session):
    """
    RED PHASE: Test that auth_audit_log table exists
    Requirements: 12.1, 12.2, 12.3
    """
    result = await db_session.execute(
        text("SELECT to_regclass('public.auth_audit_log')")
    )
    table_exists = result.scalar()
    assert table_exists is not None, "auth_audit_log table does not exist"


@pytest.mark.asyncio
async def test_auth_audit_log_has_correct_columns(db_session):
    """
    RED PHASE: Test auth_audit_log has required columns
    Requirements: 12.1, 12.2
    """
    result = await db_session.execute(
        text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'auth_audit_log'
            ORDER BY ordinal_position
        """)
    )
    columns = {row[0]: row[1] for row in result}

    required_columns = {
        "id": "integer",
        "user_id": "integer",
        "email": "character varying",
        "event_type": "character varying",
        "ip_address": "inet",
        "user_agent": "text",
        "created_at": "timestamp with time zone"
    }

    for col_name, col_type in required_columns.items():
        assert col_name in columns, f"Column {col_name} missing"
        assert columns[col_name] == col_type, \
            f"Column {col_name} has wrong type: {columns[col_name]}"


@pytest.mark.asyncio
async def test_auth_audit_log_has_indexes(db_session):
    """
    RED PHASE: Test indexes on auth_audit_log for efficient queries
    Requirements: 12.5
    """
    result = await db_session.execute(
        text("""
            SELECT indexname
            FROM pg_indexes
            WHERE tablename = 'auth_audit_log'
        """)
    )
    indexes = [row[0] for row in result]

    # Should have indexes on user_id and email for query performance
    assert len(indexes) >= 2, "Missing indexes on auth_audit_log"
