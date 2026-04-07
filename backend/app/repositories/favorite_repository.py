"""
Favorite Repository - Data access for favorites
"""
from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.favorite import Favorite


class FavoriteRepository:
    """Repository for Favorite operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_song_favorite(self, user_id: int, song_id: int) -> Favorite:
        """Add song to favorites"""
        favorite = Favorite(user_id=user_id, song_id=song_id)
        self.db.add(favorite)
        await self.db.commit()
        await self.db.refresh(favorite)
        return favorite

    async def add_album_favorite(self, user_id: int, album_id: int) -> Favorite:
        """Add album to favorites"""
        favorite = Favorite(user_id=user_id, album_id=album_id)
        self.db.add(favorite)
        await self.db.commit()
        await self.db.refresh(favorite)
        return favorite

    async def remove_song_favorite(self, user_id: int, song_id: int) -> bool:
        """Remove song from favorites"""
        result = await self.db.execute(
            select(Favorite).where(
                and_(
                    Favorite.user_id == user_id,
                    Favorite.song_id == song_id
                )
            )
        )
        favorite = result.scalar_one_or_none()

        if favorite:
            await self.db.delete(favorite)
            await self.db.commit()
            return True
        return False

    async def remove_album_favorite(self, user_id: int, album_id: int) -> bool:
        """Remove album from favorites"""
        result = await self.db.execute(
            select(Favorite).where(
                and_(
                    Favorite.user_id == user_id,
                    Favorite.album_id == album_id
                )
            )
        )
        favorite = result.scalar_one_or_none()

        if favorite:
            await self.db.delete(favorite)
            await self.db.commit()
            return True
        return False

    async def is_song_favorited(self, user_id: int, song_id: int) -> bool:
        """Check if song is favorited by user"""
        result = await self.db.execute(
            select(Favorite).where(
                and_(
                    Favorite.user_id == user_id,
                    Favorite.song_id == song_id
                )
            )
        )
        return result.scalar_one_or_none() is not None

    async def is_album_favorited(self, user_id: int, album_id: int) -> bool:
        """Check if album is favorited by user"""
        result = await self.db.execute(
            select(Favorite).where(
                and_(
                    Favorite.user_id == user_id,
                    Favorite.album_id == album_id
                )
            )
        )
        return result.scalar_one_or_none() is not None

    async def list_user_song_favorites(self, user_id: int):
        """List all favorited songs for a user with song details"""
        from app.models.song import Song
        from app.models.album import Album
        from app.models.artist import Artist

        result = await self.db.execute(
            select(Song, Album, Artist.name.label("artist_name"), Artist.id.label("artist_id"))
            .join(Favorite, Song.id == Favorite.song_id)
            .outerjoin(Album, Song.album_id == Album.id)
            .outerjoin(Artist, Album.artist_id == Artist.id)
            .where(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc())
        )

        favorites = []
        for row in result:
            song = row[0]
            album = row[1]
            artist_name = row[2]
            artist_id = row[3]
            favorites.append({
                "id": song.id,
                "title": song.title,
                "artist_id": artist_id,
                "artist_name": artist_name,
                "album_id": song.album_id,
                "duration_seconds": song.duration_seconds,
                "genre": song.genre,
            })

        return favorites

    async def list_user_album_favorites(self, user_id: int):
        """List all favorited albums for a user with album details"""
        from app.models.album import Album
        from app.models.artist import Artist

        result = await self.db.execute(
            select(Album, Artist.name.label("artist_name"))
            .join(Favorite, Album.id == Favorite.album_id)
            .outerjoin(Artist, Album.artist_id == Artist.id)
            .where(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc())
        )

        favorites = []
        for row in result:
            album = row[0]
            artist_name = row[1]
            favorites.append({
                "id": album.id,
                "title": album.title,
                "artist_id": album.artist_id,
                "artist_name": artist_name,
                "release_year": album.release_year,
                "cover_art_url": album.album_cover_url,
                "genre": album.genre,
            })

        return favorites
