"""
Album Pydantic Schemas - Task 8
Request/response schemas for Album API
Requirements: 5.1-7.6
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import List, Optional


class AlbumCreateRequest(BaseModel):
    """Request schema for creating album"""
    title: str = Field(..., min_length=1, max_length=200)
    artist_id: int = Field(..., gt=0)
    release_year: int = Field(..., ge=1900)
    album_cover_url: Optional[str] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Album title cannot be empty")
        return value.strip()


class AlbumUpdateRequest(BaseModel):
    """Request schema for updating album"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    release_year: Optional[int] = Field(None, ge=1900)
    album_cover_url: Optional[str] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            if not value.strip():
                raise ValueError("Album title cannot be empty")
            return value.strip()
        return value


class AlbumResponse(BaseModel):
    """Response schema for album"""
    id: int
    title: str
    artist_id: int
    artist_name: Optional[str]
    release_year: int
    album_cover_url: Optional[str]
    genre: Optional[str]
    songs_count: int
    total_duration_seconds: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedAlbumResponse(BaseModel):
    """Response schema for paginated album list"""
    items: List[AlbumResponse]
    total: int
    page: int
    page_size: int
