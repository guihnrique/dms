"""
Playlist API routes - Task 6
FastAPI routes for playlist operations
Requirements: 1, 2, 3, 4, 5, 6, 7, 8, 10, 11
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.playlist import verify_playlist_ownership
from app.models.user import User
from app.models.playlist import Playlist
from app.services.playlist_service import PlaylistService
from app.repositories.playlist_song_repository import PlaylistSongRepository
from app.schemas.playlist import (
    PlaylistCreateRequest,
    PlaylistUpdateRequest,
    AddSongRequest,
    ReorderSongRequest,
    PlaylistResponse,
    PlaylistListResponse,
    PlaylistSongResponse
)

router = APIRouter(prefix="/playlists", tags=["playlists"])


@router.post("", response_model=PlaylistResponse, status_code=status.HTTP_201_CREATED)
async def create_playlist(
    request: PlaylistCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new playlist

    Task 6.1: POST /playlists
    Requirements: 1 (Playlist Creation)

    Returns:
        201 Created with PlaylistResponse
    """
    service = PlaylistService(db)

    try:
        playlist = await service.create_playlist(
            title=request.title,
            owner_user_id=current_user.id,
            is_public=request.is_public
        )
        return playlist
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me", response_model=PlaylistListResponse)
async def get_my_playlists(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's playlists

    Task 6.3: GET /playlists/me (replaces /users/me/playlists)
    Requirements: 2 (Playlist Retrieval)

    Query params:
        page: Page number (default: 1)
        page_size: Items per page (default: 20, max: 100)

    Returns:
        200 OK with PlaylistListResponse

    Raises:
        401 Unauthorized if not authenticated
    """
    service = PlaylistService(db)
    result = await service.get_user_playlists(
        current_user.id,
        page=page,
        page_size=page_size
    )

    return PlaylistListResponse(**result)


@router.get("/public", response_model=PlaylistListResponse)
async def get_public_playlists(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get public playlists (no authentication required)

    Task 6.4: GET /playlists/public
    Requirements: 2, 8 (Public Playlist Retrieval)

    Query params:
        page: Page number (default: 1)
        page_size: Items per page (default: 20, max: 100)

    Returns:
        200 OK with PlaylistListResponse (only public playlists)
    """
    service = PlaylistService(db)
    result = await service.get_public_playlists(page=page, page_size=page_size)

    return PlaylistListResponse(**result)


@router.get("/{id}", response_model=PlaylistResponse)
async def get_playlist(
    id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get playlist by ID with songs (paginated)

    Task 6.2: GET /playlists/{id}
    Requirements: 2 (Playlist Retrieval), 11 (Playlist Song Details)

    Query params:
        page: Page number (default: 1)
        page_size: Items per page (default: 50, max: 100)

    Returns:
        200 OK with PlaylistResponse including paginated songs

    Raises:
        403 Forbidden if private playlist accessed by non-owner
        404 Not Found if playlist doesn't exist
    """
    service = PlaylistService(db)
    song_repo = PlaylistSongRepository(db)

    # Get playlist with privacy enforcement
    current_user_id = current_user.id if current_user else None
    playlist = await service.get_playlist_by_id(id, current_user_id=current_user_id)

    # Get paginated songs
    songs = await song_repo.get_songs(id, page=page, page_size=page_size)

    # Convert to PlaylistSongResponse
    song_responses = [
        PlaylistSongResponse(**song) for song in songs
    ]

    # Add songs to response
    playlist.songs = song_responses

    return playlist


@router.put("/{id}", response_model=PlaylistResponse)
async def update_playlist(
    id: int,
    request: PlaylistUpdateRequest,
    playlist: Playlist = Depends(verify_playlist_ownership),
    db: AsyncSession = Depends(get_db)
):
    """
    Update playlist (owner only)

    Task 6.5: PUT /playlists/{id}
    Requirements: 3 (Playlist Update), 8 (Privacy Toggle), 10 (Ownership)

    Returns:
        200 OK with updated PlaylistResponse

    Raises:
        403 Forbidden if not owner
        400 Bad Request if validation fails
    """
    service = PlaylistService(db)

    try:
        updated = await service.update_playlist(
            id,
            title=request.title,
            is_public=request.is_public
        )
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_playlist(
    id: int,
    playlist: Playlist = Depends(verify_playlist_ownership),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete playlist (owner only)

    Task 6.6: DELETE /playlists/{id}
    Requirements: 4 (Playlist Deletion), 10 (Ownership)

    Returns:
        204 No Content on success

    Raises:
        403 Forbidden if not owner
        404 Not Found if playlist doesn't exist
    """
    service = PlaylistService(db)
    await service.delete_playlist(id)
    return None


@router.post("/{id}/songs", response_model=PlaylistResponse)
async def add_song_to_playlist(
    id: int,
    request: AddSongRequest,
    playlist: Playlist = Depends(verify_playlist_ownership),
    db: AsyncSession = Depends(get_db)
):
    """
    Add song to playlist (owner only)

    Task 6.7: POST /playlists/{id}/songs
    Requirements: 5 (Add Song), 10 (Ownership), 12 (Duplicates)

    Returns:
        200 OK with updated PlaylistResponse

    Raises:
        403 Forbidden if not owner
        400 Bad Request if song not found
    """
    service = PlaylistService(db)
    updated = await service.add_song_to_playlist(id, request.song_id)
    return updated


@router.delete("/{id}/songs/{playlist_song_id}", response_model=PlaylistResponse)
async def remove_song_from_playlist(
    id: int,
    playlist_song_id: int,
    playlist: Playlist = Depends(verify_playlist_ownership),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove song from playlist (owner only, specific instance)

    Task 6.8: DELETE /playlists/{id}/songs/{playlist_song_id}
    Requirements: 6 (Remove Song), 10 (Ownership)

    Returns:
        200 OK with updated PlaylistResponse

    Raises:
        403 Forbidden if not owner
        404 Not Found if playlist_song not found
    """
    service = PlaylistService(db)
    updated = await service.remove_song_from_playlist(id, playlist_song_id)
    return updated


@router.patch("/{id}/songs/{playlist_song_id}/reorder", response_model=PlaylistResponse)
async def reorder_song(
    id: int,
    playlist_song_id: int,
    request: ReorderSongRequest,
    playlist: Playlist = Depends(verify_playlist_ownership),
    db: AsyncSession = Depends(get_db)
):
    """
    Reorder song in playlist (owner only)

    Task 6.9: PATCH /playlists/{id}/songs/{playlist_song_id}/reorder
    Requirements: 7 (Reorder Songs), 10 (Ownership)

    Returns:
        200 OK with updated PlaylistResponse

    Raises:
        403 Forbidden if not owner
        400 Bad Request if new_position out of bounds
    """
    service = PlaylistService(db)
    updated = await service.reorder_song(id, playlist_song_id, request.new_position)
    return updated
