"""
Search and Recommendation Schemas - Task 2.1, 2.2, 2.3
Requirements: 1, 2, 3, 4, 5, 6, 10, 11
"""
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class GenreEnum(str, Enum):
    """Supported music genres"""
    ROCK = "Rock"
    POP = "Pop"
    JAZZ = "Jazz"
    CLASSICAL = "Classical"
    ELECTRONIC = "Electronic"
    HIP_HOP = "Hip-Hop"
    METAL = "Metal"
    COUNTRY = "Country"
    RNB = "R&B"
    INDIE = "Indie"


class SortParameter(str, Enum):
    """Sorting parameters for search results"""
    RELEVANCE = "relevance"
    POPULARITY = "popularity"
    RELEASE_DATE = "release_date"
    RATING = "rating"


class SortOrder(str, Enum):
    """Sort order direction"""
    ASC = "asc"
    DESC = "desc"


class SearchRequest(BaseModel):
    """Search request schema with validation"""
    query: str = Field(..., min_length=2, description="Search query (min 2 characters)")
    genres: Optional[List[GenreEnum]] = Field(default=None, description="Filter by genres (OR logic)")
    year_min: Optional[int] = Field(default=None, ge=1900, description="Minimum release year")
    year_max: Optional[int] = Field(default=None, description="Maximum release year")
    sort_by: Optional[SortParameter] = Field(default=SortParameter.RELEVANCE, description="Sort parameter")
    sort_order: Optional[SortOrder] = Field(default=SortOrder.DESC, description="Sort order")

    @field_validator('year_max')
    @classmethod
    def validate_year_max(cls, v):
        """Validate year_max is not in the future"""
        if v is not None:
            from datetime import datetime
            current_year = datetime.now().year
            if v > current_year + 1:
                raise ValueError(f"year_max cannot exceed {current_year + 1}")
        return v

    @field_validator('year_min')
    @classmethod
    def validate_year_range(cls, v, info):
        """Validate year range is logical"""
        if v is not None and v < 1900:
            raise ValueError("year_min must be >= 1900")
        return v


class ArtistResult(BaseModel):
    """Artist search result"""
    id: int
    name: str
    photo_url: Optional[str] = None
    relevance_score: int = Field(..., ge=0, le=100, description="Relevance score 0-100")
    albums_count: int = Field(default=0, description="Number of albums")


class AlbumResult(BaseModel):
    """Album search result"""
    id: int
    title: str
    artist_id: int
    artist_name: str
    release_year: Optional[int]
    genre: Optional[str]
    cover_art_url: Optional[str] = None
    relevance_score: int = Field(..., ge=0, le=100, description="Relevance score 0-100")


class SongResult(BaseModel):
    """Song search result"""
    id: int
    title: str
    artist_name: str
    album_title: str
    genre: Optional[str]
    cover_art_url: Optional[str] = None
    average_rating: Optional[Decimal]
    review_count: int
    relevance_score: int = Field(..., ge=0, le=100, description="Relevance score 0-100")


class SearchResponse(BaseModel):
    """Search results response with grouped entities"""
    artists: List[ArtistResult]
    albums: List[AlbumResult]
    songs: List[SongResult]
    total_count: int = Field(..., description="Total results across all entities")


class RecommendedSong(BaseModel):
    """Recommended song with scoring"""
    song_id: int
    title: str
    artist_name: str
    album_title: str
    genre: Optional[str]
    cover_art_url: Optional[str] = None
    average_rating: Optional[Decimal]
    score: int = Field(..., ge=0, le=100, description="Recommendation score 0-100")
    reason: str = Field(..., description="Human-readable explanation")


class RecommendationResponse(BaseModel):
    """Recommendation results response"""
    recommendations: List[RecommendedSong]
    total_count: int


class FeedbackRequest(BaseModel):
    """User feedback on recommendation"""
    song_id: int
    action: str = Field(..., description="User action: accepted, dismissed, or clicked")

    @field_validator('action')
    @classmethod
    def validate_action(cls, v):
        """Validate action is one of accepted, dismissed, clicked"""
        valid_actions = ['accepted', 'dismissed', 'clicked']
        if v not in valid_actions:
            raise ValueError(f"action must be one of: {', '.join(valid_actions)}")
        return v


class UserProfile(BaseModel):
    """Internal user profile for recommendations"""
    favorite_genres: List[str]
    favorite_artists: List[int]  # Artist IDs
    playlist_song_count: int
    review_count: int
