"""
Song Router - Task 11.1-11.5
REST API endpoints for Song entity with soft delete
Requirements: 9.1-11.7
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.schemas.song import (
    SongCreateRequest,
    SongUpdateRequest,
    SongResponse,
    PaginatedSongResponse
)
from app.services.song_service import SongService
from app.dependencies.rbac import require_role
from app.models.user import User
from app.middleware.rate_limit import limiter

router = APIRouter(prefix="/api/v1/songs", tags=["songs"])


@router.post("", response_model=SongResponse, status_code=201)
@limiter.limit("10/minute")
async def create_song(
    request: Request,
    song_request: SongCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "artist"))
):
    """Create new song - Requires admin or artist role"""
    try:
        service = SongService(db)
        song = await service.create_song(
            title=song_request.title,
            album_id=song_request.album_id,
            duration_seconds=song_request.duration_seconds,
            genre=song_request.genre,
            year=song_request.year,
            external_links=song_request.external_links
        )

        return SongResponse(
            id=song.id,
            title=song.title,
            album_id=song.album_id,
            album_title=song.album_title,
            artist_id=song.artist_id,
            artist_name=song.artist_name,
            duration_seconds=song.duration_seconds,
            genre=song.genre,
            year=song.year,
            cover_art_url=song.cover_art_url,
            external_links=song.external_links,
            deleted_at=song.deleted_at,
            created_at=song.created_at,
            updated_at=song.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{song_id}", response_model=SongResponse)
async def get_song(
    song_id: int,
    include_deleted: bool = Query(False, description="Include soft-deleted songs (admin only)"),
    db: AsyncSession = Depends(get_db)
):
    """Get song by ID - Public endpoint"""
    # Only return non-deleted songs for public endpoint
    if include_deleted:
        raise HTTPException(status_code=403, detail="Use admin endpoint to view deleted songs")

    service = SongService(db)
    song = await service.get_song_by_id(song_id, include_deleted=include_deleted)

    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    return SongResponse(
        id=song.id,
        title=song.title,
        album_id=song.album_id,
        album_title=song.album_title,
        artist_id=song.artist_id,
        artist_name=song.artist_name,
        duration_seconds=song.duration_seconds,
        genre=song.genre,
        year=song.year,
        cover_art_url=song.cover_art_url,
        external_links=song.external_links,
        deleted_at=song.deleted_at,
        created_at=song.created_at,
        updated_at=song.updated_at
    )


@router.get("", response_model=PaginatedSongResponse)
async def list_songs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    album_id: Optional[int] = Query(None, description="Filter by album ID"),
    artist_id: Optional[int] = Query(None, description="Filter by artist ID"),
    db: AsyncSession = Depends(get_db)
):
    """List songs with pagination and filtering - Public endpoint"""

    service = SongService(db)
    result = await service.list_songs(
        page=page,
        page_size=page_size,
        album_id=album_id,
        artist_id=artist_id,
        include_deleted=False
    )

    responses = [
        SongResponse(
            id=song.id,
            title=song.title,
            album_id=song.album_id,
            album_title=song.album_title,
            artist_id=song.artist_id,
            artist_name=song.artist_name,
            duration_seconds=song.duration_seconds,
            genre=song.genre,
            year=song.year,
            cover_art_url=song.cover_art_url,
            external_links=song.external_links,
            deleted_at=song.deleted_at,
            created_at=song.created_at,
            updated_at=song.updated_at
        )
        for song in result["items"]
    ]

    return PaginatedSongResponse(
        items=responses,
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"]
    )


@router.put("/{song_id}", response_model=SongResponse)
async def update_song(
    song_id: int,
    song_request: SongUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "artist"))
):
    """Update song - Requires admin or artist role"""
    try:
        service = SongService(db)
        song = await service.update_song(
            song_id=song_id,
            title=song_request.title,
            duration_seconds=song_request.duration_seconds,
            genre=song_request.genre,
            year=song_request.year,
            external_links=song_request.external_links
        )

        if not song:
            raise HTTPException(status_code=404, detail="Song not found")

        return SongResponse(
            id=song.id,
            title=song.title,
            album_id=song.album_id,
            album_title=song.album_title,
            artist_id=song.artist_id,
            artist_name=song.artist_name,
            duration_seconds=song.duration_seconds,
            genre=song.genre,
            year=song.year,
            cover_art_url=song.cover_art_url,
            external_links=song.external_links,
            deleted_at=song.deleted_at,
            created_at=song.created_at,
            updated_at=song.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{song_id}", status_code=204)
async def soft_delete_song(
    song_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Soft delete song - Requires admin role"""
    service = SongService(db)
    deleted = await service.soft_delete_song(song_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Song not found")

    return None


@router.post("/{song_id}/restore", response_model=SongResponse)
async def restore_song(
    song_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Restore soft-deleted song - Requires admin role"""
    service = SongService(db)
    song = await service.restore_song(song_id)

    if not song:
        raise HTTPException(status_code=404, detail="Song not found or not deleted")

    return SongResponse(
        id=song.id,
        title=song.title,
        album_id=song.album_id,
        album_title=song.album_title,
        artist_id=song.artist_id,
        artist_name=song.artist_name,
        duration_seconds=song.duration_seconds,
        genre=song.genre,
        year=song.year,
        cover_art_url=song.cover_art_url,
        external_links=song.external_links,
        deleted_at=song.deleted_at,
        created_at=song.created_at,
        updated_at=song.updated_at
    )
