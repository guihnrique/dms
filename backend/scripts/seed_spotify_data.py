"""
Seed database with real music data from Spotify API
Populates artists, albums, and songs with actual data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime

from app.models.artist import Artist
from app.models.album import Album
from app.models.song import Song
from app.config import settings

# Spotify API setup (usando autenticação pública sem credenciais - funciona para dados públicos)
# Para produção, você deve registrar um app em https://developer.spotify.com/dashboard
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id='your_client_id',  # Substitua por suas credenciais
    client_secret='your_client_secret'  # Substitua por suas credenciais
))

# Usar autenticação sem credenciais (apenas para leitura pública)
sp = spotipy.Spotify()

# Lista de artistas populares para popular o banco
ARTISTS_TO_SEED = [
    'AC/DC',
    'Metallica',
    'Pink Floyd',
    'Led Zeppelin',
    'The Beatles',
    'Queen',
    'Nirvana',
    'Radiohead',
    'Arctic Monkeys',
    'Red Hot Chili Peppers',
    # Artistas brasileiros
    'Legião Urbana',
    'Cazuza',
    'Chico Buarque',
    'Caetano Veloso',
    'Gilberto Gil'
]

async def get_or_create_artist(session: AsyncSession, name: str, spotify_id: str = None) -> Artist:
    """Get existing artist or create new one"""
    stmt = select(Artist).where(Artist.name == name)
    result = await session.execute(stmt)
    artist = result.scalar_one_or_none()

    if not artist:
        artist = Artist(name=name, bio=f"Popular artist known for their unique sound.")
        session.add(artist)
        await session.flush()

    return artist

async def seed_from_spotify():
    """Main seed function using Spotify API"""
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            print("🎵 Starting to seed database with Spotify data...")

            for artist_name in ARTISTS_TO_SEED:
                try:
                    print(f"\n🎤 Searching for artist: {artist_name}")

                    # Search for artist
                    results = sp.search(q=f'artist:{artist_name}', type='artist', limit=1)
                    if not results['artists']['items']:
                        print(f"❌ Artist {artist_name} not found on Spotify")
                        continue

                    spotify_artist = results['artists']['items'][0]

                    # Create or get artist
                    artist = await get_or_create_artist(
                        session,
                        spotify_artist['name'],
                        spotify_artist['id']
                    )
                    print(f"✅ Artist: {artist.name} (ID: {artist.id})")

                    # Get artist's albums
                    albums_results = sp.artist_albums(
                        spotify_artist['id'],
                        album_type='album',
                        limit=5  # Limit to 5 albums per artist
                    )

                    for spotify_album in albums_results['items']:
                        # Check if album already exists
                        stmt = select(Album).where(Album.title == spotify_album['name'], Album.artist_id == artist.id)
                        result = await session.execute(stmt)
                        existing_album = result.scalar_one_or_none()

                        if existing_album:
                            print(f"  ⏭️  Album already exists: {spotify_album['name']}")
                            continue

                        # Get full album details
                        album_details = sp.album(spotify_album['id'])

                        # Create album
                        album = Album(
                            title=album_details['name'],
                            artist_id=artist.id,
                            release_year=int(album_details['release_date'][:4]) if album_details.get('release_date') else None,
                            genre=album_details['genres'][0] if album_details.get('genres') else 'Rock',
                            cover_art_url=album_details['images'][0]['url'] if album_details['images'] else None
                        )
                        session.add(album)
                        await session.flush()
                        print(f"  💿 Album: {album.title} ({album.release_year})")

                        # Add songs from album
                        for track in album_details['tracks']['items'][:15]:  # Limit to 15 songs per album
                            song = Song(
                                title=track['name'],
                                album_id=album.id,
                                track_number=track['track_number'],
                                duration_seconds=track['duration_ms'] // 1000,
                                genre=album.genre
                            )
                            session.add(song)
                            print(f"    🎵 Song: {song.title} ({song.duration_seconds}s)")

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

            print(f"\n✅ Seed completed!")
            print(f"📊 Database statistics:")
            print(f"   - Artists: {artists_count}")
            print(f"   - Albums: {albums_count}")
            print(f"   - Songs: {songs_count}")

        except Exception as e:
            print(f"❌ Fatal error: {e}")
            await session.rollback()
        finally:
            await engine.dispose()

if __name__ == "__main__":
    print("🚀 Digital Music Store - Spotify Data Seeder")
    print("=" * 50)
    asyncio.run(seed_from_spotify())
