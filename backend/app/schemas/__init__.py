"""
Pydantic schemas for request/response validation
"""
from app.schemas.auth import RegisterRequest, LoginRequest, UserResponse
from app.schemas.artist import (
    ArtistCreateRequest,
    ArtistUpdateRequest,
    ArtistResponse,
    PaginatedArtistResponse
)
from app.schemas.album import (
    AlbumCreateRequest,
    AlbumUpdateRequest,
    AlbumResponse,
    PaginatedAlbumResponse
)
from app.schemas.song import (
    SongCreateRequest,
    SongUpdateRequest,
    SongResponse,
    PaginatedSongResponse
)
from app.schemas.playlist import (
    PlaylistCreateRequest,
    PlaylistUpdateRequest,
    AddSongRequest,
    ReorderSongRequest,
    PlaylistResponse,
    PlaylistSongResponse,
    PlaylistListResponse
)
from app.schemas.review import (
    ReviewCreateRequest,
    ReviewUpdateRequest,
    VoteRequest,
    ReviewResponse,
    ReviewListResponse,
    SongWithReviewsResponse
)

__all__ = [
    "RegisterRequest",
    "LoginRequest",
    "UserResponse",
    "ArtistCreateRequest",
    "ArtistUpdateRequest",
    "ArtistResponse",
    "PaginatedArtistResponse",
    "AlbumCreateRequest",
    "AlbumUpdateRequest",
    "AlbumResponse",
    "PaginatedAlbumResponse",
    "SongCreateRequest",
    "SongUpdateRequest",
    "SongResponse",
    "PaginatedSongResponse",
    "PlaylistCreateRequest",
    "PlaylistUpdateRequest",
    "AddSongRequest",
    "ReorderSongRequest",
    "PlaylistResponse",
    "PlaylistSongResponse",
    "PlaylistListResponse"
]
