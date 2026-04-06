"""
Artist Repository - Task 3.1, 3.2, 3.3
Data access layer for Artist entity with CRUD, pagination, and search
Requirements: 1.1-4.7, 3.1-3.6, 13.1
"""
from typing import List, Tuple, Optional, Dict, Any
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.artist import Artist
from app.models.album import Album


class ArtistRepository:
    """
    Repository for Artist entity operations

    Requirements:
    - 1.1-4.7: CRUD operations
    - 2.2-2.5: Pagination with default 20, max 100
    - 2.7: Include albums_count
    - 3.1-3.6: Search with case-insensitive partial match
    - 13.1: Performance (<200ms for 10k records)
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session

        Args:
            db: SQLAlchemy async session
        """
        self.db = db

    async def create(self, name: str, country: str) -> Artist:
        """
        Create new artist

        Requirements:
        - 1.1: Create artist record
        - 1.4: Timestamps automatically set

        Args:
            name: Artist name (1-200 characters)
            country: ISO 3166-1 alpha-2 country code

        Returns:
            Artist: Created artist with generated ID
        """
        artist = Artist(name=name, country=country)
        self.db.add(artist)
        await self.db.commit()
        await self.db.refresh(artist)
        return artist

    async def get_by_id(self, artist_id: int) -> Optional[Artist]:
        """
        Get artist by ID

        Requirements:
        - 2.1: Retrieve artist by ID
        - 2.6: Return None if not found

        Args:
            artist_id: Artist ID

        Returns:
            Optional[Artist]: Artist if found, None otherwise
        """
        result = await self.db.execute(
            select(Artist).where(Artist.id == artist_id)
        )
        return result.scalar_one_or_none()

    async def update(self, artist_id: int, **kwargs) -> Optional[Artist]:
        """
        Update artist record

        Requirements:
        - 4.1: Update artist record
        - 4.2: Update updated_at timestamp (automatic via trigger)
        - 4.3: Do not modify created_at

        Args:
            artist_id: Artist ID
            **kwargs: Fields to update (name, country)

        Returns:
            Optional[Artist]: Updated artist if found, None otherwise
        """
        artist = await self.get_by_id(artist_id)
        if not artist:
            return None

        # Update fields
        for key, value in kwargs.items():
            if hasattr(artist, key):
                setattr(artist, key, value)

        await self.db.commit()
        await self.db.refresh(artist)
        return artist

    async def list_paginated(
        self,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Artist], int]:
        """
        List artists with pagination

        Requirements:
        - 2.2: Paginated results
        - 2.3: Default page size of 20
        - 2.4: Maximum page size of 100

        Args:
            page: Page number (starts at 1)
            page_size: Number of items per page (max 100)

        Returns:
            Tuple[List[Artist], int]: (artists, total_count)
        """
        # Enforce max page size
        page_size = min(page_size, 100)

        # Calculate offset
        offset = (page - 1) * page_size

        # Get paginated items
        result = await self.db.execute(
            select(Artist)
            .order_by(Artist.name)
            .limit(page_size)
            .offset(offset)
        )
        items = result.scalars().all()

        # Get total count
        count_result = await self.db.execute(
            select(func.count()).select_from(Artist)
        )
        total = count_result.scalar()

        return list(items), total

    async def get_artists_with_albums_count(
        self,
        artist_ids: List[int]
    ) -> List[Dict[str, Any]]:
        """
        Get artists with albums count

        Requirements:
        - 2.7: Include albums_count field

        Args:
            artist_ids: List of artist IDs

        Returns:
            List[Dict]: Artists with albums_count
        """
        result = await self.db.execute(
            select(
                Artist.id,
                Artist.name,
                Artist.country,
                Artist.created_at,
                Artist.updated_at,
                func.count(Album.id).label("albums_count")
            )
            .outerjoin(Album, Artist.id == Album.artist_id)
            .where(Artist.id.in_(artist_ids))
            .group_by(Artist.id)
        )

        artists = []
        for row in result:
            artists.append({
                "id": row.id,
                "name": row.name,
                "country": row.country,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
                "albums_count": row.albums_count
            })

        return artists

    async def search(
        self,
        query: str,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Artist], int]:
        """
        Search artists by name with trigram index

        Requirements:
        - 3.1: Case-insensitive partial match
        - 3.3: Return paginated results
        - 3.4: Performance <200ms for 10k records
        - 3.5: Return empty array when no results
        - 3.6: Sanitize input (SQLAlchemy parameterized queries)

        Args:
            query: Search query (min 2 characters)
            page: Page number (starts at 1)
            page_size: Number of items per page

        Returns:
            Tuple[List[Artist], int]: (matching artists, total_count)
        """
        # Sanitize query (trim whitespace, prevent empty)
        query = query.strip()
        if not query:
            return [], 0

        # Enforce max page size
        page_size = min(page_size, 100)

        # Calculate offset
        offset = (page - 1) * page_size

        # Use ILIKE for case-insensitive partial match
        # SQLAlchemy parameterized queries prevent SQL injection
        search_pattern = f"%{query}%"

        # Get matching items
        result = await self.db.execute(
            select(Artist)
            .where(Artist.name.ilike(search_pattern))
            .order_by(Artist.name)
            .limit(page_size)
            .offset(offset)
        )
        items = result.scalars().all()

        # Get total count
        count_result = await self.db.execute(
            select(func.count())
            .select_from(Artist)
            .where(Artist.name.ilike(search_pattern))
        )
        total = count_result.scalar()

        return list(items), total
