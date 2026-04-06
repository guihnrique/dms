"""
Playlist dependencies - Task 5.1
FastAPI dependencies for playlist operations
Requirements: 3, 4, 5, 6, 7, 10
"""
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.playlist import Playlist
from app.repositories.playlist_repository import PlaylistRepository


async def verify_playlist_ownership(
    playlist_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Playlist:
    """
    Verify playlist ownership

    Args:
        playlist_id: Playlist ID from path
        current_user: Current authenticated user
        db: Database session

    Returns:
        Playlist if user is owner

    Raises:
        HTTPException: 404 if playlist not found, 403 if not owner

    Requirements:
    - 3: Playlist Update (owner only)
    - 4: Playlist Delete (owner only)
    - 5: Add Song (owner only)
    - 6: Remove Song (owner only)
    - 7: Reorder Songs (owner only)
    - 10: Ownership verification for mutations
    """
    # Get playlist
    repo = PlaylistRepository(db)
    playlist = await repo.get_by_id(playlist_id)

    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    # Verify ownership
    if playlist.owner_user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not own this playlist"
        )

    return playlist
