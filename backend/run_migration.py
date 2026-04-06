"""
Script to run SQL migrations using asyncpg
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()


async def run_migration(migration_file: str):
    """
    Run SQL migration file

    Args:
        migration_file: Path to SQL migration file
    """
    # Get connection string (convert from SQLAlchemy format to asyncpg format)
    database_url = os.getenv("DATABASE_URL")
    # Convert postgresql+asyncpg:// to postgresql://
    database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")

    print(f"Running migration: {migration_file}")
    print(f"Connecting to database...")

    # Read migration file
    with open(migration_file, "r") as f:
        sql = f.read()

    # Connect and execute
    conn = await asyncpg.connect(database_url, ssl="require")

    try:
        # Execute the entire migration as a single transaction
        print("Executing migration...")
        await conn.execute(sql)
        print("\n✅ Migration completed successfully!")

    finally:
        await conn.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python run_migration.py <migration_file>")
        sys.exit(1)

    migration_file = sys.argv[1]
    asyncio.run(run_migration(migration_file))
