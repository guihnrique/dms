"""
Favorites Router - Endpoints for managing user favorites
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.repositories.favorite_repository import FavoriteRepository
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/favorites", tags=["Favorites"])


@router.post("/songs/{song_id}", status_code=status.HTTP_201_CREATED)
async def favorite_song(
    song_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add song to favorites"""
    repo = FavoriteRepository(db)

    # Check if already favorited
    if await repo.is_song_favorited(current_user.id, song_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Song already in favorites"
        )

    await repo.add_song_favorite(current_user.id, song_id)
    return {"message": "Song added to favorites", "favorited": True}


@router.delete("/songs/{song_id}", status_code=status.HTTP_200_OK)
async def unfavorite_song(
    song_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove song from favorites"""
    repo = FavoriteRepository(db)

    removed = await repo.remove_song_favorite(current_user.id, song_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )

    return {"message": "Song removed from favorites", "favorited": False}


@router.get("/songs/{song_id}/status")
async def check_song_favorite_status(
    song_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if song is favorited"""
    repo = FavoriteRepository(db)
    is_favorited = await repo.is_song_favorited(current_user.id, song_id)
    return {"favorited": is_favorited}


@router.post("/albums/{album_id}", status_code=status.HTTP_201_CREATED)
async def favorite_album(
    album_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add album to favorites"""
    repo = FavoriteRepository(db)

    # Check if already favorited
    if await repo.is_album_favorited(current_user.id, album_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Album already in favorites"
        )

    await repo.add_album_favorite(current_user.id, album_id)
    return {"message": "Album added to favorites", "favorited": True}


@router.delete("/albums/{album_id}", status_code=status.HTTP_200_OK)
async def unfavorite_album(
    album_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove album from favorites"""
    repo = FavoriteRepository(db)

    removed = await repo.remove_album_favorite(current_user.id, album_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )

    return {"message": "Album removed from favorites", "favorited": False}


@router.get("/albums/{album_id}/status")
async def check_album_favorite_status(
    album_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if album is favorited"""
    repo = FavoriteRepository(db)
    is_favorited = await repo.is_album_favorited(current_user.id, album_id)
    return {"favorited": is_favorited}


@router.get("/songs")
async def list_favorite_songs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all favorited songs for current user"""
    repo = FavoriteRepository(db)
    favorites = await repo.list_user_song_favorites(current_user.id)
    return {"items": favorites, "total": len(favorites)}


@router.get("/albums")
async def list_favorite_albums(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all favorited albums for current user"""
    repo = FavoriteRepository(db)
    favorites = await repo.list_user_album_favorites(current_user.id)
    return {"items": favorites, "total": len(favorites)}
