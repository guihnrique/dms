"""
Artist Service - Task 4.1-4.4
Business logic layer for Artist entity with validation
Requirements: 1.1-4.7, 14.1-14.2
"""
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.artist_repository import ArtistRepository
from app.services.validation_service import ValidationService
from app.models.artist import Artist


class ArtistResponse:
    """Artist response with albums count"""
    def __init__(self, artist: Artist, albums_count: int = 0):
        self.id = artist.id
        self.name = artist.name
        self.country = artist.country
        self.created_at = artist.created_at
        self.updated_at = artist.updated_at
        self.albums_count = albums_count


class ArtistService:
    """
    Business logic for Artist operations

    Requirements:
    - 1.1-1.8: Artist creation with validation
    - 2.1-2.8: Artist retrieval
    - 3.1-3.6: Artist search
    - 4.1-4.7: Artist update
    - 14.1-14.2: Text sanitization
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize service with database session

        Args:
            db: SQLAlchemy async session
        """
        self.db = db
        self.artist_repo = ArtistRepository(db)
        self.validation_service = ValidationService()

    async def create_artist(self, name: str, country: str) -> ArtistResponse:
        """
        Create new artist with validation

        Requirements:
        - 1.1: Create artist record
        - 1.2: Validate name length (1-200 characters)
        - 1.3: Validate country code (ISO 3166-1 alpha-2)
        - 14.1: Reject empty strings
        - 14.2: Trim whitespace

        Args:
            name: Artist name
            country: ISO 3166-1 alpha-2 country code

        Returns:
            ArtistResponse: Created artist with albums_count=0

        Raises:
            ValueError: If validation fails
        """
        # Sanitize name (trim whitespace, reject empty)
        name = self.validation_service.sanitize_text(name)

        # Validate name length
        if len(name) > 200:
            raise ValueError("Artist name must be at most 200 characters")

        # Normalize and validate country code
        country = country.upper().strip()
        if not self.validation_service.validate_country_code(country):
            raise ValueError(f"Invalid country code: {country}")

        # Create artist
        artist = await self.artist_repo.create(name=name, country=country)

        # Return response with albums_count=0 (new artist has no albums)
        return ArtistResponse(artist, albums_count=0)

    async def get_artist_by_id(self, artist_id: int) -> Optional[ArtistResponse]:
        """
        Get artist by ID with albums count

        Requirements:
        - 2.1: Retrieve artist by ID
        - 2.7: Include albums_count field

        Args:
            artist_id: Artist ID

        Returns:
            Optional[ArtistResponse]: Artist with albums count if found, None otherwise
        """
        # Get artist
        artist = await self.artist_repo.get_by_id(artist_id)
        if not artist:
            return None

        # Get albums count
        artists_with_count = await self.artist_repo.get_artists_with_albums_count([artist_id])

        if not artists_with_count:
            return ArtistResponse(artist, albums_count=0)

        # Return response with albums count
        albums_count = artists_with_count[0]["albums_count"]
        return ArtistResponse(artist, albums_count=albums_count)

    async def search_artists(
        self,
        query: str,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        Search artists by name

        Requirements:
        - 3.1: Case-insensitive partial match
        - 3.2: Reject queries less than 2 characters
        - 3.3: Return paginated results
        - 3.5: Return empty array when no results
        - 3.6: Sanitize input

        Args:
            query: Search query (min 2 characters)
            page: Page number
            page_size: Items per page

        Returns:
            Dict: {items: List[ArtistResponse], total: int, page: int, page_size: int}

        Raises:
            ValueError: If query is too short
        """
        # Sanitize query
        query = query.strip()

        # Validate minimum length
        if len(query) < 2:
            raise ValueError("Search query must be at least 2 characters")

        # Search
        items, total = await self.artist_repo.search(query=query, page=page, page_size=page_size)

        # Get albums counts for all found artists
        if items:
            artist_ids = [artist.id for artist in items]
            artists_with_count = await self.artist_repo.get_artists_with_albums_count(artist_ids)

            # Create map of artist_id -> albums_count
            albums_count_map = {a["id"]: a["albums_count"] for a in artists_with_count}

            # Build responses
            responses = [
                ArtistResponse(artist, albums_count=albums_count_map.get(artist.id, 0))
                for artist in items
            ]
        else:
            responses = []

        return {
            "items": responses,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    async def update_artist(
        self,
        artist_id: int,
        name: Optional[str] = None,
        country: Optional[str] = None
    ) -> Optional[ArtistResponse]:
        """
        Update artist with validation

        Requirements:
        - 4.1: Update artist record
        - 4.2: Update updated_at timestamp (automatic via trigger)
        - 4.3: Do not modify created_at
        - 4.7: Apply same validation rules as creation

        Args:
            artist_id: Artist ID
            name: New name (optional)
            country: New country code (optional)

        Returns:
            Optional[ArtistResponse]: Updated artist if found, None otherwise

        Raises:
            ValueError: If validation fails
        """
        # Build update data
        update_data = {}

        # Validate and sanitize name if provided
        if name is not None:
            name = self.validation_service.sanitize_text(name)
            if len(name) > 200:
                raise ValueError("Artist name must be at most 200 characters")
            update_data["name"] = name

        # Validate country code if provided
        if country is not None:
            country = country.upper().strip()
            if not self.validation_service.validate_country_code(country):
                raise ValueError(f"Invalid country code: {country}")
            update_data["country"] = country

        # Update artist
        artist = await self.artist_repo.update(artist_id, **update_data)
        if not artist:
            return None

        # Get albums count
        artists_with_count = await self.artist_repo.get_artists_with_albums_count([artist_id])
        albums_count = artists_with_count[0]["albums_count"] if artists_with_count else 0

        return ArtistResponse(artist, albums_count=albums_count)
