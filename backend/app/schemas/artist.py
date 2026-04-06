"""
Artist Pydantic Schemas - Task 5
Request/response schemas for Artist API
Requirements: 1.1-4.7, 2.1-2.8
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import List, Optional


class ArtistCreateRequest(BaseModel):
    """
    Request schema for creating artist

    Requirements:
    - 1.2: Name 1-200 characters
    - 1.3: Country ISO 3166-1 alpha-2
    """
    name: str = Field(..., min_length=1, max_length=200, description="Artist name")
    country: str = Field(..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code")

    @field_validator('name')
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Validate name is not empty or whitespace"""
        if not value or not value.strip():
            raise ValueError("Artist name cannot be empty or whitespace-only")
        return value.strip()

    @field_validator('country')
    @classmethod
    def validate_country(cls, value: str) -> str:
        """Normalize country code to uppercase"""
        return value.upper().strip()


class ArtistUpdateRequest(BaseModel):
    """
    Request schema for updating artist

    Requirements:
    - 4.1: Partial update (optional fields)
    - 4.7: Same validation rules as creation
    """
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Artist name")
    country: Optional[str] = Field(None, min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code")

    @field_validator('name')
    @classmethod
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        """Validate name if provided"""
        if value is not None:
            if not value.strip():
                raise ValueError("Artist name cannot be empty or whitespace-only")
            return value.strip()
        return value

    @field_validator('country')
    @classmethod
    def validate_country(cls, value: Optional[str]) -> Optional[str]:
        """Normalize country code if provided"""
        if value is not None:
            return value.upper().strip()
        return value


class ArtistResponse(BaseModel):
    """
    Response schema for artist

    Requirements:
    - 2.7: Include albums_count field
    """
    id: int
    name: str
    country: str
    albums_count: int = Field(..., description="Number of albums by this artist")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedArtistResponse(BaseModel):
    """
    Response schema for paginated artist list

    Requirements:
    - 2.2: Paginated results
    """
    items: List[ArtistResponse]
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
