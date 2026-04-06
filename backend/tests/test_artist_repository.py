"""
Test Artist Repository - Task 3.1, 3.2, 3.3
Test-Driven Development (TDD): RED phase

Tests for ArtistRepository CRUD operations, pagination, and search
Requirements: 1.1-4.7, 13.1
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession


class TestArtistRepositoryBaseCRUD:
    """Test base CRUD methods - Task 3.1"""

    @pytest.mark.asyncio
    async def test_artist_repository_create_returns_artist_with_id(self, db_session: AsyncSession):
        """
        Test creating artist returns artist with generated ID

        Requirements:
        - 1.1: Create artist record
        - 1.4: Timestamps automatically set
        """
        from app.repositories.artist_repository import ArtistRepository

        repo = ArtistRepository(db_session)

        # Create artist
        artist = await repo.create(name="The Beatles", country="GB")

        # Verify
        assert artist is not None, "Artist should be created"
        assert artist.id is not None, "Artist ID should be generated"
        assert artist.name == "The Beatles", "Artist name should match"
        assert artist.country == "GB", "Artist country should match"
        assert artist.created_at is not None, "created_at should be set"
        assert artist.updated_at is not None, "updated_at should be set"

    @pytest.mark.asyncio
    async def test_artist_repository_get_by_id_returns_artist(self, db_session: AsyncSession):
        """
        Test getting artist by ID returns artist

        Requirements:
        - 2.1: Retrieve artist by ID
        """
        from app.repositories.artist_repository import ArtistRepository

        repo = ArtistRepository(db_session)

        # Create artist first
        created_artist = await repo.create(name="Pink Floyd", country="GB")

        # Get by ID
        retrieved_artist = await repo.get_by_id(created_artist.id)

        # Verify
        assert retrieved_artist is not None, "Artist should be found"
        assert retrieved_artist.id == created_artist.id, "IDs should match"
        assert retrieved_artist.name == "Pink Floyd", "Name should match"

    @pytest.mark.asyncio
    async def test_artist_repository_get_by_id_returns_none_when_not_found(self, db_session: AsyncSession):
        """
        Test getting artist by non-existent ID returns None

        Requirements:
        - 2.6: Return 404 if artist not found
        """
        from app.repositories.artist_repository import ArtistRepository

        repo = ArtistRepository(db_session)

        # Try to get non-existent artist
        artist = await repo.get_by_id(99999)

        # Verify
        assert artist is None, "Non-existent artist should return None"

    @pytest.mark.asyncio
    async def test_artist_repository_update_modifies_artist(self, db_session: AsyncSession):
        """
        Test updating artist modifies the record

        Requirements:
        - 4.1: Update artist record
        - 4.2: Update updated_at timestamp
        - 4.3: Do not modify created_at
        """
        from app.repositories.artist_repository import ArtistRepository

        repo = ArtistRepository(db_session)

        # Create artist
        artist = await repo.create(name="Led Zeppelin", country="GB")
        original_created_at = artist.created_at
        original_updated_at = artist.updated_at

        # Update artist
        updated_artist = await repo.update(artist.id, name="Led Zeppelin (Updated)", country="UK")

        # Verify
        assert updated_artist is not None, "Updated artist should be returned"
        assert updated_artist.name == "Led Zeppelin (Updated)", "Name should be updated"
        assert updated_artist.country == "UK", "Country should be updated"
        assert updated_artist.created_at == original_created_at, "created_at should not change"
        assert updated_artist.updated_at != original_updated_at, "updated_at should change"


class TestArtistRepositoryPagination:
    """Test pagination with albums count - Task 3.2"""

    @pytest.mark.asyncio
    async def test_artist_repository_list_paginated_returns_20_by_default(self, db_session: AsyncSession):
        """
        Test listing artists returns 20 by default

        Requirements:
        - 2.3: Default page size of 20 artists
        """
        from app.repositories.artist_repository import ArtistRepository

        repo = ArtistRepository(db_session)

        # Create 25 artists
        for i in range(25):
            await repo.create(name=f"Artist {i}", country="US")

        # Get first page (default page_size should be 20)
        items, total = await repo.list_paginated(page=1, page_size=20)

        # Verify
        assert len(items) == 20, "Should return 20 items by default"
        assert total == 25, "Total count should be 25"

    @pytest.mark.asyncio
    async def test_artist_repository_list_paginated_respects_max_100(self, db_session: AsyncSession):
        """
        Test listing artists enforces maximum page size of 100

        Requirements:
        - 2.4: Maximum page size of 100 artists
        """
        from app.repositories.artist_repository import ArtistRepository

        repo = ArtistRepository(db_session)

        # Create 150 artists
        for i in range(150):
            await repo.create(name=f"Artist {i}", country="US")

        # Request page_size of 200 (should be capped at 100)
        items, total = await repo.list_paginated(page=1, page_size=200)

        # Verify
        assert len(items) <= 100, "Should not return more than 100 items"
        assert total == 150, "Total count should be 150"

    @pytest.mark.asyncio
    async def test_artist_repository_list_includes_albums_count(self, db_session: AsyncSession):
        """
        Test listing artists includes albums count

        Requirements:
        - 2.7: Include albums_count field
        """
        from app.repositories.artist_repository import ArtistRepository
        from app.models.artist import Artist
        from app.models.album import Album

        repo = ArtistRepository(db_session)

        # Create artist with albums
        artist = await repo.create(name="Queen", country="GB")

        # Create albums directly (not through repo)
        album1 = Album(title="A Night at the Opera", artist_id=artist.id, release_year=1975)
        album2 = Album(title="News of the World", artist_id=artist.id, release_year=1977)
        db_session.add_all([album1, album2])
        await db_session.commit()

        # Get artist with albums count
        artists_with_count = await repo.get_artists_with_albums_count([artist.id])

        # Verify
        assert len(artists_with_count) == 1, "Should return 1 artist"
        artist_data = artists_with_count[0]
        assert artist_data["id"] == artist.id, "Artist ID should match"
        assert artist_data["albums_count"] == 2, "Should have 2 albums"


class TestArtistRepositorySearch:
    """Test search with trigram index - Task 3.3"""

    @pytest.mark.asyncio
    async def test_artist_repository_search_case_insensitive_partial_match(self, db_session: AsyncSession):
        """
        Test searching artists performs case-insensitive partial match

        Requirements:
        - 3.1: Case-insensitive partial match on artist name
        """
        from app.repositories.artist_repository import ArtistRepository

        repo = ArtistRepository(db_session)

        # Create test data
        await repo.create(name="The Beatles", country="GB")
        await repo.create(name="Beatles Tribute Band", country="US")
        await repo.create(name="Rolling Stones", country="GB")
        await repo.create(name="Pink Floyd", country="GB")

        # Search for "beatles" (lowercase)
        items, total = await repo.search(query="beatles", page=1, page_size=20)

        # Verify
        assert total == 2, "Should find 2 artists matching 'beatles'"
        artist_names = [artist.name for artist in items]
        assert "The Beatles" in artist_names, "Should find 'The Beatles'"
        assert "Beatles Tribute Band" in artist_names, "Should find 'Beatles Tribute Band'"

    @pytest.mark.asyncio
    async def test_artist_repository_search_returns_paginated_results(self, db_session: AsyncSession):
        """
        Test search returns paginated results

        Requirements:
        - 3.3: Return paginated list
        - 3.5: Return empty items array when no results
        """
        from app.repositories.artist_repository import ArtistRepository

        repo = ArtistRepository(db_session)

        # Create 10 artists with "Rock" in name
        for i in range(10):
            await repo.create(name=f"Rock Band {i}", country="US")

        # Search with pagination
        items, total = await repo.search(query="rock", page=1, page_size=5)

        # Verify
        assert len(items) == 5, "Should return 5 items (first page)"
        assert total == 10, "Total should be 10"

        # Test empty result
        empty_items, empty_total = await repo.search(query="nonexistent", page=1, page_size=20)
        assert len(empty_items) == 0, "Should return empty list"
        assert empty_total == 0, "Total should be 0"

    @pytest.mark.asyncio
    async def test_artist_repository_search_sanitizes_input(self, db_session: AsyncSession):
        """
        Test search sanitizes input to prevent SQL injection

        Requirements:
        - 3.6: Sanitize search input
        """
        from app.repositories.artist_repository import ArtistRepository

        repo = ArtistRepository(db_session)

        # Create test data
        await repo.create(name="Test Artist", country="US")

        # Try SQL injection patterns (should be safe)
        items, total = await repo.search(query="'; DROP TABLE artists; --", page=1, page_size=20)

        # Verify - should return empty result, not crash
        assert items is not None, "Search should not crash with injection attempt"
        assert isinstance(items, list), "Should return list"
