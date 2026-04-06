"""
Album Router - Task 8.1-8.3
REST API endpoints for Album entity
Requirements: 5.1-7.6
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.schemas.album import (
    AlbumCreateRequest,
    AlbumUpdateRequest,
    AlbumResponse,
    PaginatedAlbumResponse
)
from app.services.album_service import AlbumService
from app.dependencies.rbac import require_role
from app.models.user import User
from app.middleware.rate_limit import limiter

router = APIRouter(prefix="/api/v1/albums", tags=["albums"])


@router.post("", response_model=AlbumResponse, status_code=201)
@limiter.limit("10/minute")
async def create_album(
    request: Request,
    album_request: AlbumCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "artist"))
):
    """Create new album - Requires admin or artist role"""
    try:
        service = AlbumService(db)
        album = await service.create_album(
            title=album_request.title,
            artist_id=album_request.artist_id,
            release_year=album_request.release_year,
            album_cover_url=album_request.album_cover_url
        )

        return AlbumResponse(
            id=album.id,
            title=album.title,
            artist_id=album.artist_id,
            artist_name=album.artist_name,
            release_year=album.release_year,
            album_cover_url=album.album_cover_url,
            songs_count=album.songs_count,
            total_duration_seconds=album.total_duration_seconds,
            created_at=album.created_at,
            updated_at=album.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{album_id}", response_model=AlbumResponse)
async def get_album(
    album_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get album by ID - Public endpoint"""
    service = AlbumService(db)
    album = await service.get_album_by_id(album_id)

    if not album:
        raise HTTPException(status_code=404, detail="Album not found")

    return AlbumResponse(
        id=album.id,
        title=album.title,
        artist_id=album.artist_id,
        artist_name=album.artist_name,
        release_year=album.release_year,
        album_cover_url=album.album_cover_url,
        songs_count=album.songs_count,
        total_duration_seconds=album.total_duration_seconds,
        created_at=album.created_at,
        updated_at=album.updated_at
    )


@router.get("", response_model=PaginatedAlbumResponse)
async def list_albums(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    artist_id: Optional[int] = Query(None, description="Filter by artist ID"),
    db: AsyncSession = Depends(get_db)
):
    """List albums with pagination and filtering - Public endpoint"""
    service = AlbumService(db)
    result = await service.list_albums(page=page, page_size=page_size, artist_id=artist_id)

    responses = [
        AlbumResponse(
            id=album.id,
            title=album.title,
            artist_id=album.artist_id,
            artist_name=album.artist_name,
            release_year=album.release_year,
            album_cover_url=album.album_cover_url,
            songs_count=album.songs_count,
            total_duration_seconds=album.total_duration_seconds,
            created_at=album.created_at,
            updated_at=album.updated_at
        )
        for album in result["items"]
    ]

    return PaginatedAlbumResponse(
        items=responses,
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"]
    )


@router.put("/{album_id}", response_model=AlbumResponse)
async def update_album(
    album_id: int,
    album_request: AlbumUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "artist"))
):
    """Update album - Requires admin or artist role"""
    try:
        service = AlbumService(db)
        album = await service.update_album(
            album_id=album_id,
            title=album_request.title,
            release_year=album_request.release_year,
            album_cover_url=album_request.album_cover_url
        )

        if not album:
            raise HTTPException(status_code=404, detail="Album not found")

        return AlbumResponse(
            id=album.id,
            title=album.title,
            artist_id=album.artist_id,
            artist_name=album.artist_name,
            release_year=album.release_year,
            album_cover_url=album.album_cover_url,
            songs_count=album.songs_count,
            total_duration_seconds=album.total_duration_seconds,
            created_at=album.created_at,
            updated_at=album.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
