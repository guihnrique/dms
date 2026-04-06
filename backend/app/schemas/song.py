"""
Song Pydantic Schemas - Task 11
Request/response schemas for Song API with soft delete support
Requirements: 9.1-11.7
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import List, Optional


class SongCreateRequest(BaseModel):
    """Request schema for creating song"""
    title: str = Field(..., min_length=1, max_length=200)
    album_id: int = Field(..., gt=0)
    duration_seconds: int = Field(..., ge=1, le=7200)
    genre: Optional[str] = Field(None, max_length=50)
    year: Optional[int] = Field(None, ge=1900)
    external_links: Optional[dict] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Song title cannot be empty")
        return value.strip()

    @field_validator('genre')
    @classmethod
    def validate_genre(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            if not value.strip():
                raise ValueError("Genre cannot be empty if provided")
            return value.strip()
        return value


class SongUpdateRequest(BaseModel):
    """Request schema for updating song"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    duration_seconds: Optional[int] = Field(None, ge=1, le=7200)
    genre: Optional[str] = Field(None, max_length=50)
    year: Optional[int] = Field(None, ge=1900)
    external_links: Optional[dict] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            if not value.strip():
                raise ValueError("Song title cannot be empty")
            return value.strip()
        return value

    @field_validator('genre')
    @classmethod
    def validate_genre(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            if not value.strip():
                raise ValueError("Genre cannot be empty if provided")
            return value.strip()
        return value


class SongResponse(BaseModel):
    """Response schema for song"""
    id: int
    title: str
    album_id: int
    album_title: Optional[str]
    artist_id: Optional[int]
    artist_name: Optional[str]
    duration_seconds: int
    genre: Optional[str]
    year: Optional[int]
    external_links: Optional[dict]
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedSongResponse(BaseModel):
    """Response schema for paginated song list"""
    items: List[SongResponse]
    total: int
    page: int
    page_size: int
