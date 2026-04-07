"""
Clean database and reseed with only real music data
Removes all test/dummy data and repopulates with real artists
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import delete, select, func

from app.models.artist import Artist
from app.models.album import Album
from app.models.song import Song
from app.models.review import Review, ReviewVote
from app.models.playlist import Playlist, PlaylistSong
from app.models.favorite import Favorite
from app.database import DATABASE_URL

async def clean_database():
    """Remove all music catalog data (keeps users)"""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            print("\n🧹 Cleaning database...")
            print("=" * 60)

            # Delete in correct order (respecting foreign keys)
            print("  🗑️  Deleting favorites...")
            await session.execute(delete(Favorite))

            print("  🗑️  Deleting playlist songs...")
            await session.execute(delete(PlaylistSong))

            print("  🗑️  Deleting playlists...")
            await session.execute(delete(Playlist))

            print("  🗑️  Deleting review votes...")
            await session.execute(delete(ReviewVote))

            print("  🗑️  Deleting reviews...")
            await session.execute(delete(Review))

            print("  🗑️  Deleting songs...")
            await session.execute(delete(Song))

            print("  🗑️  Deleting albums...")
            await session.execute(delete(Album))

            print("  🗑️  Deleting artists...")
            await session.execute(delete(Artist))

            await session.commit()
            print("✅ Database cleaned successfully!")

        except Exception as e:
            print(f"❌ Error cleaning database: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()

async def verify_clean():
    """Verify database is clean"""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        result = await session.execute(select(func.count()).select_from(Artist))
        artists = result.scalar()

        result = await session.execute(select(func.count()).select_from(Album))
        albums = result.scalar()

        result = await session.execute(select(func.count()).select_from(Song))
        songs = result.scalar()

        print(f"\n📊 Database Status After Cleaning:")
        print(f"   Artists: {artists}")
        print(f"   Albums: {albums}")
        print(f"   Songs: {songs}")

        await engine.dispose()

        if artists == 0 and albums == 0 and songs == 0:
            print("✅ Database is clean and ready for seeding!")
            return True
        else:
            print("⚠️  Warning: Some data still remains")
            return False

async def main():
    print("\n" + "=" * 60)
    print("🧹 Digital Music Store - Database Cleanup & Reseed")
    print("=" * 60)

    try:
        # Clean database
        await clean_database()

        # Verify clean
        is_clean = await verify_clean()

        if is_clean:
            print("\n" + "=" * 60)
            print("🚀 Now run: python scripts/quick_seed.py")
            print("   Or run: python scripts/seed_real_data.py")
            print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
