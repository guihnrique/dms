"""
Seed database with real music data from MusicBrainz API
Populates artists, albums, and songs with actual data
No API key required - completely free!
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import musicbrainzngs as mb
import time
import random

from app.models.artist import Artist
from app.models.album import Album
from app.models.song import Song
from app.database import DATABASE_URL

# Configure MusicBrainz
mb.set_useragent("DigitalMusicStore", "1.0", "contact@example.com")

# Lista de artistas populares para popular o banco
ARTISTS_TO_SEED = [
    # Rock Clássico Internacional
    ('AC/DC', 'Rock'),
    ('Metallica', 'Metal'),
    ('Pink Floyd', 'Progressive Rock'),
    ('Led Zeppelin', 'Rock'),
    ('The Beatles', 'Rock'),
    ('Queen', 'Rock'),
    ('Nirvana', 'Grunge'),
    ('Radiohead', 'Alternative Rock'),
    ('Arctic Monkeys', 'Indie Rock'),
    ('Red Hot Chili Peppers', 'Alternative Rock'),
    ('The Rolling Stones', 'Rock'),
    ('Black Sabbath', 'Metal'),

    # Rock/MPB Brasileiro
    ('Legião Urbana', 'Rock'),
    ('Cazuza', 'Rock'),
    ('Titãs', 'Rock'),
    ('Capital Inicial', 'Rock'),
    ('Os Paralamas do Sucesso', 'Rock'),
    ('Chico Buarque', 'MPB'),
    ('Caetano Veloso', 'MPB'),
    ('Gilberto Gil', 'MPB'),
    ('Marisa Monte', 'MPB'),
    ('Gal Costa', 'MPB'),

    # Pop/Eletrônica
    ('Daft Punk', 'Electronic'),
    ('The Weeknd', 'Pop'),
    ('Coldplay', 'Alternative Rock'),
    ('Imagine Dragons', 'Pop Rock'),
]

async def get_or_create_artist(session: AsyncSession, name: str, genre: str, bio: str = None) -> Artist:
    """Get existing artist or create new one"""
    stmt = select(Artist).where(Artist.name == name)
    result = await session.execute(stmt)
    artist = result.scalar_one_or_none()

    if not artist:
        artist = Artist(
            name=name,
            bio=bio or f"Renowned {genre} artist with a unique sound and influential discography."
        )
        session.add(artist)
        await session.flush()

    return artist

async def seed_from_musicbrainz():
    """Main seed function using MusicBrainz API"""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            print("🎵 Starting to seed database with MusicBrainz data...")
            print("=" * 60)

            for artist_name, default_genre in ARTISTS_TO_SEED:
                try:
                    print(f"\n🎤 Searching for artist: {artist_name}")

                    # Rate limiting - MusicBrainz requires 1 request per second
                    time.sleep(1)

                    # Search for artist
                    result = mb.search_artists(artist=artist_name, limit=1)

                    if not result['artist-list']:
                        print(f"❌ Artist '{artist_name}' not found")
                        continue

                    mb_artist = result['artist-list'][0]

                    # Create or get artist
                    artist = await get_or_create_artist(
                        session,
                        mb_artist['name'],
                        default_genre,
                        mb_artist.get('disambiguation', '')
                    )
                    print(f"✅ Artist: {artist.name} (ID: {artist.id})")

                    # Get artist's albums (releases)
                    time.sleep(1)
                    releases_result = mb.browse_releases(
                        artist=mb_artist['id'],
                        release_type=['album'],
                        limit=5
                    )

                    if not releases_result.get('release-list'):
                        print(f"  ⚠️  No albums found for {artist_name}")
                        continue

                    for mb_release in releases_result['release-list']:
                        # Check if album already exists
                        stmt = select(Album).where(
                            Album.title == mb_release['title'],
                            Album.artist_id == artist.id
                        )
                        result_album = await session.execute(stmt)
                        existing_album = result_album.scalar_one_or_none()

                        if existing_album:
                            print(f"  ⏭️  Album already exists: {mb_release['title']}")
                            continue

                        # Extract year from date
                        release_year = None
                        if mb_release.get('date'):
                            try:
                                release_year = int(mb_release['date'][:4])
                            except (ValueError, IndexError):
                                pass

                        # Create album
                        album = Album(
                            title=mb_release['title'],
                            artist_id=artist.id,
                            release_year=release_year,
                            genre=default_genre
                        )
                        session.add(album)
                        await session.flush()
                        print(f"  💿 Album: {album.title} ({album.release_year or 'Unknown year'})")

                        # Get tracks for this release
                        time.sleep(1)
                        try:
                            release_details = mb.get_release_by_id(
                                mb_release['id'],
                                includes=['recordings']
                            )

                            if 'medium-list' in release_details['release']:
                                track_number = 1
                                songs_added = 0

                                for medium in release_details['release']['medium-list']:
                                    if 'track-list' not in medium:
                                        continue

                                    for track in medium['track-list'][:15]:  # Limit to 15 songs
                                        recording = track.get('recording', {})

                                        # Get duration (convert from milliseconds)
                                        duration_ms = recording.get('length')
                                        duration_seconds = int(duration_ms) // 1000 if duration_ms else random.randint(180, 300)

                                        song = Song(
                                            title=recording.get('title', track.get('title', 'Unknown')),
                                            album_id=album.id,
                                            track_number=track_number,
                                            duration_seconds=duration_seconds,
                                            genre=default_genre
                                        )
                                        session.add(song)
                                        songs_added += 1
                                        track_number += 1

                                        if songs_added >= 15:
                                            break

                                if songs_added > 0:
                                    print(f"    🎵 Added {songs_added} songs")

                        except Exception as e:
                            print(f"    ⚠️  Could not fetch tracks: {e}")
                            # Add some placeholder songs if we can't get real ones
                            for i in range(1, min(11, 15)):
                                song = Song(
                                    title=f"Track {i}",
                                    album_id=album.id,
                                    track_number=i,
                                    duration_seconds=random.randint(180, 300),
                                    genre=default_genre
                                )
                                session.add(song)
                            print(f"    🎵 Added 10 placeholder songs")

                        await session.flush()

                    await session.commit()
                    print(f"✅ Completed seeding for {artist_name}")

                except Exception as e:
                    print(f"❌ Error seeding {artist_name}: {e}")
                    await session.rollback()
                    continue

            # Get statistics
            stmt_artists = select(Artist)
            result_artists = await session.execute(stmt_artists)
            artists_count = len(result_artists.scalars().all())

            stmt_albums = select(Album)
            result_albums = await session.execute(stmt_albums)
            albums_count = len(result_albums.scalars().all())

            stmt_songs = select(Song).where(Song.deleted_at.is_(None))
            result_songs = await session.execute(stmt_songs)
            songs_count = len(result_songs.scalars().all())

            print(f"\n" + "=" * 60)
            print(f"✅ Seed completed successfully!")
            print(f"\n📊 Database statistics:")
            print(f"   - Artists: {artists_count}")
            print(f"   - Albums: {albums_count}")
            print(f"   - Songs: {songs_count}")
            print(f"\n🚀 Your Digital Music Store is ready with real data!")

        except Exception as e:
            print(f"❌ Fatal error: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
        finally:
            await engine.dispose()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🎸 Digital Music Store - Real Music Data Seeder")
    print("📚 Using MusicBrainz API (Free & No Auth Required)")
    print("=" * 60 + "\n")
    asyncio.run(seed_from_musicbrainz())
