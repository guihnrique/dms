"""
Script to populate album genres in the database
"""
import asyncio
import random
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import os
from dotenv import load_dotenv

# Add parent directory to path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.album import Album

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

# Common electronic music genres
GENRES = [
    'Synthwave',
    'Techno',
    'House',
    'Trance',
    'Ambient',
    'Drum & Bass',
    'Dubstep',
    'Electro',
    'IDM',
    'Breakbeat',
]

async def main():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # Get all albums
        result = await session.execute(select(Album))
        albums = result.scalars().all()

        print(f"Found {len(albums)} albums")

        # Count albums without genre
        without_genre = [a for a in albums if not a.genre]
        print(f"Albums without genre: {len(without_genre)}")

        if without_genre:
            print("\nPopulating genres...")
            for album in without_genre:
                album.genre = random.choice(GENRES)
                print(f"  {album.title} -> {album.genre}")

            await session.commit()
            print(f"\n✓ Updated {len(without_genre)} albums with genres")
        else:
            print("\nAll albums already have genres!")

        # Show distribution
        print("\nGenre distribution:")
        result = await session.execute(select(Album))
        all_albums = result.scalars().all()
        genre_count = {}
        for album in all_albums:
            if album.genre:
                genre_count[album.genre] = genre_count.get(album.genre, 0) + 1

        for genre, count in sorted(genre_count.items()):
            print(f"  {genre}: {count}")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
