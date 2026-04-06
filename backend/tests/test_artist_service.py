"""
Test Artist Service - Task 4.1-4.4
Test-Driven Development (TDD): RED phase

Tests for ArtistService business logic with validation
Requirements: 1.1-4.7, 14.1-14.2
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession


class TestArtistServiceCreate:
    """Test artist creation with validation - Task 4.1"""

    @pytest.mark.asyncio
    async def test_artist_service_create_validates_name_length(self, db_session: AsyncSession):
        """
        Test that artist creation validates name length (1-200 characters)

        Requirements:
        - 1.2: Validate name length
        - 14.1: Reject empty strings
        """
        from app.services.artist_service import ArtistService

        service = ArtistService(db_session)

        # Test empty name
        with pytest.raises(ValueError, match="cannot be empty"):
            await service.create_artist(name="", country="US")

        # Test whitespace-only name
        with pytest.raises(ValueError, match="cannot be empty"):
            await service.create_artist(name="   ", country="US")

        # Test name too long (over 200 characters)
        long_name = "A" * 201
        with pytest.raises(ValueError, match="200 characters"):
            await service.create_artist(name=long_name, country="US")

    @pytest.mark.asyncio
    async def test_artist_service_create_validates_country_code(self, db_session: AsyncSession):
        """
        Test that artist creation validates country code

        Requirements:
        - 1.3: Validate country code (ISO 3166-1 alpha-2)
        - 1.8: Return error for invalid country code
        """
        from app.services.artist_service import ArtistService

        service = ArtistService(db_session)

        # Test invalid country code
        with pytest.raises(ValueError, match="Invalid country code"):
            await service.create_artist(name="Test Artist", country="XX")

        with pytest.raises(ValueError, match="Invalid country code"):
            await service.create_artist(name="Test Artist", country="ABC")

    @pytest.mark.asyncio
    async def test_artist_service_create_sanitizes_name(self, db_session: AsyncSession):
        """
        Test that artist creation sanitizes name (trims whitespace)

        Requirements:
        - 14.2: Trim leading and trailing whitespace
        """
        from app.services.artist_service import ArtistService

        service = ArtistService(db_session)

        # Create artist with whitespace
        artist = await service.create_artist(name="  The Beatles  ", country="GB")

        # Verify name is trimmed
        assert artist.name == "The Beatles", "Name should be trimmed"
        assert artist.country == "GB", "Country should be uppercase"

    @pytest.mark.asyncio
    async def test_artist_service_create_returns_artist_with_albums_count(self, db_session: AsyncSession):
        """
        Test that artist creation returns artist response with albums_count=0

        Requirements:
        - 1.1: Create artist record
        - 2.7: Include albums_count field
        """
        from app.services.artist_service import ArtistService

        service = ArtistService(db_session)

        # Create artist
        response = await service.create_artist(name="Pink Floyd", country="GB")

        # Verify response
        assert response is not None, "Response should not be None"
        assert hasattr(response, "id"), "Response should have id"
        assert hasattr(response, "name"), "Response should have name"
        assert hasattr(response, "albums_count"), "Response should have albums_count"
        assert response.albums_count == 0, "New artist should have 0 albums"


class TestArtistServiceRetrieve:
    """Test artist retrieval - Task 4.2"""

    @pytest.mark.asyncio
    async def test_artist_service_get_by_id_includes_albums_count(self, db_session: AsyncSession):
        """
        Test that get by ID includes albums count

        Requirements:
        - 2.1: Retrieve artist by ID
        - 2.7: Include albums_count field
        """
        from app.services.artist_service import ArtistService
        from app.models.album import Album

        service = ArtistService(db_session)

        # Create artist
        artist = await service.create_artist(name="Queen", country="GB")

        # Add albums directly
        album1 = Album(title="A Night at the Opera", artist_id=artist.id, release_year=1975)
        album2 = Album(title="News of the World", artist_id=artist.id, release_year=1977)
        db_session.add_all([album1, album2])
        await db_session.commit()

        # Get artist with albums count
        response = await service.get_artist_by_id(artist.id)

        # Verify
        assert response is not None, "Should find artist"
        assert response.albums_count == 2, "Should have 2 albums"

    @pytest.mark.asyncio
    async def test_artist_service_get_by_id_returns_none_when_not_found(self, db_session: AsyncSession):
        """
        Test that get by ID returns None when artist not found

        Requirements:
        - 2.6: Return None if artist not found
        """
        from app.services.artist_service import ArtistService

        service = ArtistService(db_session)

        # Try to get non-existent artist
        response = await service.get_artist_by_id(99999)

        # Verify
        assert response is None, "Should return None for non-existent artist"


class TestArtistServiceSearch:
    """Test artist search - Task 4.3"""

    @pytest.mark.asyncio
    async def test_artist_service_search_rejects_short_query(self, db_session: AsyncSession):
        """
        Test that search rejects queries less than 2 characters

        Requirements:
        - 3.2: Reject queries less than 2 characters
        """
        from app.services.artist_service import ArtistService

        service = ArtistService(db_session)

        # Test short query
        with pytest.raises(ValueError, match="at least 2 characters"):
            await service.search_artists(query="A", page=1, page_size=20)

        # Test empty query
        with pytest.raises(ValueError, match="at least 2 characters"):
            await service.search_artists(query="", page=1, page_size=20)

    @pytest.mark.asyncio
    async def test_artist_service_search_sanitizes_input(self, db_session: AsyncSession):
        """
        Test that search sanitizes input

        Requirements:
        - 3.6: Sanitize search input to prevent SQL injection
        """
        from app.services.artist_service import ArtistService

        service = ArtistService(db_session)

        # Create test artist
        await service.create_artist(name="Test Artist", country="US")

        # Try SQL injection pattern (should be sanitized and return safely)
        response = await service.search_artists(query="'; DROP TABLE artists; --", page=1, page_size=20)

        # Verify - should return empty result, not crash
        assert response is not None, "Search should not crash"
        assert "items" in response, "Response should have items"
        assert isinstance(response["items"], list), "Items should be a list"

    @pytest.mark.asyncio
    async def test_artist_service_search_returns_paginated_results(self, db_session: AsyncSession):
        """
        Test that search returns paginated results

        Requirements:
        - 3.3: Return paginated results
        - 3.5: Return empty array when no results
        """
        from app.services.artist_service import ArtistService

        service = ArtistService(db_session)

        # Create test artists
        await service.create_artist(name="The Beatles", country="GB")
        await service.create_artist(name="Beatles Tribute Band", country="US")

        # Search
        response = await service.search_artists(query="beatles", page=1, page_size=20)

        # Verify
        assert "items" in response, "Response should have items"
        assert "total" in response, "Response should have total"
        assert len(response["items"]) == 2, "Should find 2 artists"
        assert response["total"] == 2, "Total should be 2"


class TestArtistServiceUpdate:
    """Test artist update - Task 4.4"""

    @pytest.mark.asyncio
    async def test_artist_service_update_modifies_updated_at(self, db_session: AsyncSession):
        """
        Test that update modifies updated_at timestamp

        Requirements:
        - 4.2: Update updated_at timestamp
        """
        from app.services.artist_service import ArtistService
        import asyncio

        service = ArtistService(db_session)

        # Create artist
        artist = await service.create_artist(name="Led Zeppelin", country="GB")
        original_updated_at = artist.updated_at

        # Wait a bit to ensure timestamp difference
        await asyncio.sleep(0.1)

        # Update artist
        updated = await service.update_artist(artist.id, name="Led Zeppelin (Updated)")

        # Verify
        assert updated is not None, "Update should return artist"
        assert updated.updated_at > original_updated_at, "updated_at should be later"

    @pytest.mark.asyncio
    async def test_artist_service_update_preserves_created_at(self, db_session: AsyncSession):
        """
        Test that update preserves created_at timestamp

        Requirements:
        - 4.3: Do not modify created_at
        """
        from app.services.artist_service import ArtistService

        service = ArtistService(db_session)

        # Create artist
        artist = await service.create_artist(name="AC/DC", country="AU")
        original_created_at = artist.created_at

        # Update artist
        updated = await service.update_artist(artist.id, name="AC/DC (Updated)")

        # Verify
        assert updated.created_at == original_created_at, "created_at should not change"

    @pytest.mark.asyncio
    async def test_artist_service_update_validates_fields(self, db_session: AsyncSession):
        """
        Test that update applies same validation rules as creation

        Requirements:
        - 4.7: Validate updated fields using same rules
        """
        from app.services.artist_service import ArtistService

        service = ArtistService(db_session)

        # Create artist
        artist = await service.create_artist(name="Test Artist", country="US")

        # Try to update with invalid country code
        with pytest.raises(ValueError, match="Invalid country code"):
            await service.update_artist(artist.id, country="XX")

        # Try to update with empty name
        with pytest.raises(ValueError, match="cannot be empty"):
            await service.update_artist(artist.id, name="")
