"""
Artist Router - Task 5.1-5.5
REST API endpoints for Artist entity
Requirements: 1.1-4.7, 2.1-2.8, 3.1-3.5
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.schemas.artist import (
    ArtistCreateRequest,
    ArtistUpdateRequest,
    ArtistResponse,
    PaginatedArtistResponse
)
from app.services.artist_service import ArtistService
from app.dependencies.auth import get_current_user
from app.dependencies.rbac import require_role
from app.models.user import User
from app.middleware.rate_limit import limiter

router = APIRouter(prefix="/api/v1/artists", tags=["artists"])


@router.post("", response_model=ArtistResponse, status_code=201)
@limiter.limit("10/minute")
async def create_artist(
    request: Request,
    artist_request: ArtistCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "artist"))
):
    """
    Create new artist

    Requirements:
    - 1.1: Authenticated user with admin or artist role can create
    - 1.5: Return 201 Created with artist details
    - 1.6: Return 403 for insufficient permissions (handled by require_role)
    - 1.7: Return 400 for validation errors
    - 1.8: Return 400 for invalid country code

    **Requires**: admin or artist role
    """
    try:
        service = ArtistService(db)
        artist = await service.create_artist(
            name=artist_request.name,
            country=artist_request.country
        )

        # Convert service response to API response
        return ArtistResponse(
            id=artist.id,
            name=artist.name,
            country=artist.country,
            albums_count=artist.albums_count,
            created_at=artist.created_at,
            updated_at=artist.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{artist_id}", response_model=ArtistResponse)
async def get_artist(
    artist_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get artist by ID

    Requirements:
    - 2.1: Retrieve artist by ID
    - 2.6: Return 404 if artist not found
    - 2.7: Include albums_count field
    - 2.8: Allow guest and authenticated users

    **Public endpoint** - No authentication required
    """
    service = ArtistService(db)
    artist = await service.get_artist_by_id(artist_id)

    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    return ArtistResponse(
        id=artist.id,
        name=artist.name,
        country=artist.country,
        albums_count=artist.albums_count,
        created_at=artist.created_at,
        updated_at=artist.updated_at
    )


@router.get("", response_model=PaginatedArtistResponse)
async def list_artists(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    db: AsyncSession = Depends(get_db)
):
    """
    List artists with pagination

    Requirements:
    - 2.2: Return paginated results
    - 2.3: Default page size of 20
    - 2.4: Maximum page size of 100
    - 2.8: Allow guest and authenticated users

    **Public endpoint** - No authentication required
    """
    service = ArtistService(db)
    items, total = await service.artist_repo.list_paginated(page=page, page_size=page_size)

    # Get albums counts
    if items:
        artist_ids = [artist.id for artist in items]
        artists_with_count = await service.artist_repo.get_artists_with_albums_count(artist_ids)
        albums_count_map = {a["id"]: a["albums_count"] for a in artists_with_count}

        responses = [
            ArtistResponse(
                id=artist.id,
                name=artist.name,
                country=artist.country,
                albums_count=albums_count_map.get(artist.id, 0),
                created_at=artist.created_at,
                updated_at=artist.updated_at
            )
            for artist in items
        ]
    else:
        responses = []

    return PaginatedArtistResponse(
        items=responses,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/search", response_model=PaginatedArtistResponse)
async def search_artists(
    q: str = Query(..., min_length=2, description="Search query (minimum 2 characters)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
    """
    Search artists by name

    Requirements:
    - 3.1: Case-insensitive partial match
    - 3.2: Reject queries less than 2 characters
    - 3.3: Return paginated results
    - 3.5: Return 200 OK with empty items array when no results
    - 2.8: Allow guest and authenticated users

    **Public endpoint** - No authentication required
    """
    try:
        service = ArtistService(db)
        result = await service.search_artists(query=q, page=page, page_size=page_size)

        # Convert service responses to API responses
        responses = [
            ArtistResponse(
                id=artist.id,
                name=artist.name,
                country=artist.country,
                albums_count=artist.albums_count,
                created_at=artist.created_at,
                updated_at=artist.updated_at
            )
            for artist in result["items"]
        ]

        return PaginatedArtistResponse(
            items=responses,
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{artist_id}", response_model=ArtistResponse)
async def update_artist(
    artist_id: int,
    artist_request: ArtistUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "artist"))
):
    """
    Update artist

    Requirements:
    - 4.1: Update artist record
    - 4.4: Return 200 OK with updated artist
    - 4.5: Return 403 for insufficient permissions (handled by require_role)
    - 4.6: Return 404 if artist not found
    - 4.7: Apply same validation rules as creation

    **Requires**: admin or artist role
    """
    try:
        service = ArtistService(db)
        artist = await service.update_artist(
            artist_id=artist_id,
            name=artist_request.name,
            country=artist_request.country
        )

        if not artist:
            raise HTTPException(status_code=404, detail="Artist not found")

        return ArtistResponse(
            id=artist.id,
            name=artist.name,
            country=artist.country,
            albums_count=artist.albums_count,
            created_at=artist.created_at,
            updated_at=artist.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
