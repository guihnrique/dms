"""
Quick seed with sample data - For immediate testing
Adds a few artists with realistic data without API calls
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.models.artist import Artist
from app.models.album import Album
from app.models.song import Song
from app.database import DATABASE_URL

# Sample data structure
SAMPLE_DATA = [
    {
        'artist': 'AC/DC',
        'genre': 'Rock',
        'bio': 'Australian rock band known for their hard-hitting sound and electrifying performances.',
        'albums': [
            {
                'title': 'Back in Black',
                'year': 1980,
                'songs': [
                    ('Hells Bells', 312, 1),
                    ('Shoot to Thrill', 317, 2),
                    ('What Do You Do for Money Honey', 215, 3),
                    ('Given the Dog a Bone', 210, 4),
                    ('Let Me Put My Love into You', 254, 5),
                    ('Back in Black', 255, 6),
                    ('You Shook Me All Night Long', 210, 7),
                    ('Have a Drink on Me', 238, 8),
                    ('Shake a Leg', 245, 9),
                    ('Rock and Roll Ain\'t Noise Pollution', 255, 10),
                ]
            },
            {
                'title': 'Highway to Hell',
                'year': 1979,
                'songs': [
                    ('Highway to Hell', 208, 1),
                    ('Girls Got Rhythm', 203, 2),
                    ('Walk All Over You', 311, 3),
                    ('Touch Too Much', 266, 4),
                    ('Beating Around the Bush', 236, 5),
                    ('Shot Down in Flames', 202, 6),
                    ('Get It Hot', 154, 7),
                    ('If You Want Blood (You\'ve Got It)', 277, 8),
                    ('Love Hungry Man', 257, 9),
                    ('Night Prowler', 386, 10),
                ]
            }
        ]
    },
    {
        'artist': 'Legião Urbana',
        'genre': 'Rock',
        'bio': 'Banda brasileira de rock formada em Brasília, uma das mais influentes da música brasileira.',
        'albums': [
            {
                'title': 'Dois',
                'year': 1986,
                'songs': [
                    ('Eduardo e Mônica', 287, 1),
                    ('Quase sem Querer', 254, 2),
                    ('Tempo Perdido', 319, 3),
                    ('Índios', 453, 4),
                    ('Fábrica', 270, 5),
                    ('Metrópole', 281, 6),
                    ('Que País é Este', 236, 7),
                    ('Música de Trabalho', 193, 8),
                    ('Química', 319, 9),
                ]
            },
            {
                'title': 'As Quatro Estações',
                'year': 1989,
                'songs': [
                    ('Há Tempos', 311, 1),
                    ('Pais e Filhos', 331, 2),
                    ('Feedback Song for a Dying Friend', 235, 3),
                    ('Quando o Sol Bater na Janela do Teu Quarto', 291, 4),
                    ('Sete Cidades', 264, 5),
                    ('Se Fiquei Esperando Meu Amor Passar', 274, 6),
                    ('Maurício', 168, 7),
                    ('Montanhas Navais', 236, 8),
                ]
            }
        ]
    },
    {
        'artist': 'Pink Floyd',
        'genre': 'Progressive Rock',
        'bio': 'English rock band known for philosophical lyrics, sonic experimentation, and elaborate live shows.',
        'albums': [
            {
                'title': 'The Dark Side of the Moon',
                'year': 1973,
                'songs': [
                    ('Speak to Me', 68, 1),
                    ('Breathe (In the Air)', 169, 2),
                    ('On the Run', 216, 3),
                    ('Time', 413, 4),
                    ('The Great Gig in the Sky', 283, 5),
                    ('Money', 382, 6),
                    ('Us and Them', 462, 7),
                    ('Any Colour You Like', 205, 8),
                    ('Brain Damage', 228, 9),
                    ('Eclipse', 123, 10),
                ]
            }
        ]
    },
    {
        'artist': 'The Beatles',
        'genre': 'Rock',
        'bio': 'English rock band regarded as the most influential band of all time.',
        'albums': [
            {
                'title': 'Abbey Road',
                'year': 1969,
                'songs': [
                    ('Come Together', 259, 1),
                    ('Something', 183, 2),
                    ('Maxwell\'s Silver Hammer', 207, 3),
                    ('Oh! Darling', 206, 4),
                    ('Octopus\'s Garden', 171, 5),
                    ('I Want You (She\'s So Heavy)', 467, 6),
                    ('Here Comes the Sun', 185, 7),
                    ('Because', 165, 8),
                ]
            }
        ]
    },
    {
        'artist': 'Queen',
        'genre': 'Rock',
        'bio': 'British rock band known for their flamboyant style and powerful vocals.',
        'albums': [
            {
                'title': 'A Night at the Opera',
                'year': 1975,
                'songs': [
                    ('Death on Two Legs', 223, 1),
                    ('Lazing on a Sunday Afternoon', 70, 2),
                    ('I\'m in Love with My Car', 183, 3),
                    ('You\'re My Best Friend', 170, 4),
                    ('\'39', 212, 5),
                    ('Sweet Lady', 244, 6),
                    ('Seaside Rendezvous', 136, 7),
                    ('The Prophet\'s Song', 505, 8),
                    ('Love of My Life', 218, 9),
                    ('Good Company', 207, 10),
                    ('Bohemian Rhapsody', 355, 11),
                    ('God Save the Queen', 73, 12),
                ]
            }
        ]
    }
]

async def quick_seed():
    """Quick seed with sample data"""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            print("\n🚀 Digital Music Store - Quick Seed")
            print("=" * 60)
            print("Adding sample artists with realistic data...\n")

            for data in SAMPLE_DATA:
                # Check if artist exists
                stmt = select(Artist).where(Artist.name == data['artist']).limit(1)
                result = await session.execute(stmt)
                artist = result.scalars().first()

                if not artist:
                    artist = Artist(
                        name=data['artist'],
                        country='US'  # Default country
                    )
                    session.add(artist)
                    await session.flush()
                    print(f"✅ Added artist: {artist.name}")
                else:
                    print(f"⏭️  Artist already exists: {artist.name}")

                for album_data in data['albums']:
                    # Check if album exists
                    stmt_album = select(Album).where(
                        Album.title == album_data['title'],
                        Album.artist_id == artist.id
                    )
                    result_album = await session.execute(stmt_album)
                    album = result_album.scalar_one_or_none()

                    if not album:
                        album = Album(
                            title=album_data['title'],
                            artist_id=artist.id,
                            release_year=album_data['year'],
                            genre=data['genre'],
                            album_cover_url=None  # Will be set after flush to use album.id
                        )
                        session.add(album)
                        await session.flush()

                        # Set cover URL using album ID for consistent placeholder images
                        album.album_cover_url = f"https://picsum.photos/seed/{album.id}/640/640"
                        print(f"  💿 Added album: {album.title} ({album.release_year})")

                        # Add songs
                        songs_added = 0
                        for song_title, duration, _ in album_data['songs']:
                            song = Song(
                                title=song_title,
                                album_id=album.id,
                                duration_seconds=duration,
                                genre=data['genre']
                            )
                            session.add(song)
                            songs_added += 1

                        await session.flush()
                        print(f"    🎵 Added {songs_added} songs")
                    else:
                        print(f"  ⏭️  Album already exists: {album.title}")

            await session.commit()

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
            print(f"✅ Quick seed completed!")
            print(f"\n📊 Database statistics:")
            print(f"   - Artists: {artists_count}")
            print(f"   - Albums: {albums_count}")
            print(f"   - Songs: {songs_count}")
            print(f"\n🎸 Your app is ready with real music data!")
            print(f"   Visit: http://localhost:5173")

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(quick_seed())
