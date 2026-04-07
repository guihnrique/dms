"""
Pydantic schemas for playlist endpoints - Task 2.1, 2.2
Request and response validation schemas
Requirements: 1, 2, 3, 5, 7, 8, 11
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class PlaylistCreateRequest(BaseModel):
    """
    Request schema for creating a new playlist

    Requirements:
    - 1: Playlist Creation with title validation (1-200 chars)
    - 8: Privacy Control with default private
    """
    title: str = Field(..., min_length=1, max_length=200, description="Playlist name (1-200 characters)")
    is_public: bool = Field(default=False, description="Privacy setting: True=public, False=private")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """
        Trim whitespace and reject whitespace-only strings
        Task 2.1: Implement custom validators
        """
        # Trim whitespace
        v = v.strip()

        # Reject if empty after trimming
        if not v:
            raise ValueError("Title cannot be empty or whitespace-only")

        return v

    class Config:
        json_schema_extra = {
            "example": {
                "title": "My Awesome Playlist",
                "is_public": False
            }
        }


class PlaylistUpdateRequest(BaseModel):
    """
    Request schema for updating a playlist

    Requirements:
    - 3: Playlist Update with optional fields
    - 8: Privacy Control toggle
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Updated playlist name")
    is_public: Optional[bool] = Field(None, description="Updated privacy setting")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Trim whitespace and reject whitespace-only strings"""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Title cannot be empty or whitespace-only")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Updated Playlist Name",
                "is_public": True
            }
        }


class AddSongRequest(BaseModel):
    """
    Request schema for adding a song to playlist

    Requirement: 5 (Add Song to Playlist)
    """
    song_id: int = Field(..., description="ID of song to add to playlist")

    class Config:
        json_schema_extra = {
            "example": {
                "song_id": 42
            }
        }


class ReorderSongRequest(BaseModel):
    """
    Request schema for reordering a song within playlist

    Requirement: 7 (Reorder Songs)
    """
    new_position: int = Field(..., ge=1, description="New position for song (1-indexed)")

    class Config:
        json_schema_extra = {
            "example": {
                "new_position": 3
            }
        }


class PlaylistSongResponse(BaseModel):
    """
    Response schema for playlist song with full details

    Requirement: 11 (Playlist Song Details)
    """
    playlist_song_id: int = Field(..., description="Unique ID for this playlist-song entry")
    position: int = Field(..., description="Position in playlist (1, 2, 3, ...)")
    song_id: int = Field(..., description="Song ID")
    song_title: str = Field(..., description="Song title")
    artist_name: str = Field(..., description="Artist name")
    album_id: int = Field(..., description="Album ID")
    album_title: str = Field(..., description="Album title")
    duration_seconds: int = Field(..., description="Song duration in seconds")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "playlist_song_id": 123,
                "position": 1,
                "song_id": 42,
                "song_title": "Bohemian Rhapsody",
                "artist_name": "Queen",
                "album_title": "A Night at the Opera",
                "duration_seconds": 354
            }
        }


class PlaylistResponse(BaseModel):
    """
    Response schema for playlist with metadata

    Requirement: 2 (Playlist Retrieval)
    """
    id: int = Field(..., description="Playlist ID")
    title: str = Field(..., description="Playlist name")
    owner_user_id: int = Field(..., description="Owner user ID")
    is_public: bool = Field(..., description="Privacy setting")
    songs_count: int = Field(..., description="Number of songs in playlist")
    total_duration_seconds: int = Field(..., description="Total duration of all songs")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    songs: Optional[List[PlaylistSongResponse]] = Field(default=None, description="Songs in playlist (paginated)")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "My Awesome Playlist",
                "owner_user_id": 42,
                "is_public": False,
                "songs_count": 15,
                "total_duration_seconds": 3600,
                "created_at": "2024-04-06T10:00:00Z",
                "updated_at": "2024-04-06T12:30:00Z",
                "songs": []
            }
        }


class PlaylistListResponse(BaseModel):
    """
    Response schema for paginated playlist list

    Requirement: 2 (Playlist Retrieval with pagination)
    """
    items: List[PlaylistResponse] = Field(..., description="Playlists in current page")
    total: int = Field(..., description="Total number of playlists")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")

    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 100,
                "page": 1,
                "page_size": 20,
                "total_pages": 5
            }
        }
