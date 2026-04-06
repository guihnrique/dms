"""
Run database migrations on Neon PostgreSQL
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


async def run_migration():
    """Execute migration SQL on Neon database"""
    print(f"Connecting to database...")

    engine = create_async_engine(DATABASE_URL, echo=True)

    # Read migration file
    with open("migrations/001_create_auth_tables.sql", "r") as f:
        migration_sql = f.read()

    try:
        async with engine.begin() as conn:
            print("\n🚀 Running migration 001_create_auth_tables.sql...")

            # Execute entire migration as single statement (handles dollar-quoted functions correctly)
            print(f"\nExecuting migration...")
            await conn.execute(text(migration_sql))

            print("\n✅ Migration completed successfully!")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        await engine.dispose()


async def verify_tables():
    """Verify that tables were created"""
    print("\n🔍 Verifying tables...")

    engine = create_async_engine(DATABASE_URL, echo=False)

    try:
        async with engine.begin() as conn:
            # Check users table
            result = await conn.execute(
                text("SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename IN ('users', 'auth_audit_log')")
            )
            tables = [row[0] for row in result]

            print(f"\n📋 Tables found: {tables}")

            if 'users' in tables:
                print("  ✅ users table exists")
            else:
                print("  ❌ users table missing")

            if 'auth_audit_log' in tables:
                print("  ✅ auth_audit_log table exists")
            else:
                print("  ❌ auth_audit_log table missing")

            # Check indexes
            result = await conn.execute(
                text("SELECT indexname FROM pg_indexes WHERE tablename='users'")
            )
            indexes = [row[0] for row in result]
            print(f"\n🔍 Indexes on users: {indexes}")

    finally:
        await engine.dispose()


if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE MIGRATION - Neon PostgreSQL")
    print("=" * 60)

    asyncio.run(run_migration())
    asyncio.run(verify_tables())

    print("\n" + "=" * 60)
    print("✅ Setup complete! You can now run tests.")
    print("=" * 60)
