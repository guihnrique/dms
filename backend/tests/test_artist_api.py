"""
Test Artist API Endpoints - Task 5.1-5.5
Test-Driven Development (TDD): RED phase - Integration tests

Tests for Artist REST API with authorization
Requirements: 1.1-4.7, 2.1-2.8, 3.1-3.5
"""
import pytest
from httpx import AsyncClient


class TestArtistCreationEndpoint:
    """Test artist creation endpoint - Task 5.1, 5.2"""

    @pytest.mark.asyncio
    async def test_create_artist_requires_artist_or_admin_role(self, async_client: AsyncClient):
        """
        Test that artist creation requires artist or admin role

        Requirements:
        - 1.1: Authenticated user with admin or artist role can create
        - 1.6: Return 403 for insufficient permissions
        """
        # Register and login as regular user
        register_data = {"email": f"user_{id(self)}@test.com", "password": "Test123!@#"}
        await async_client.post("/api/v1/auth/register", json=register_data)

        login_response = await async_client.post("/api/v1/auth/login", json=register_data)
        assert login_response.status_code == 200

        # Try to create artist as regular user (should fail)
        artist_data = {"name": "The Beatles", "country": "GB"}
        response = await async_client.post("/api/v1/artists", json=artist_data)

        # Verify
        assert response.status_code == 403, "Regular user should not be able to create artist"
        assert "Insufficient permissions" in response.json()["detail"] or "Access denied" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_create_artist_returns_201_with_valid_data(self, async_client: AsyncClient):
        """
        Test that artist creation returns 201 with valid data

        Requirements:
        - 1.1: Create artist record
        - 1.5: Return 201 Created with artist details
        """
        # For this test, we need to create an admin/artist user
        # Since we don't have easy admin creation in tests, we'll skip role check for now
        # and test the endpoint functionality

        # This test will be updated once we have proper admin user creation
        pytest.skip("Requires admin user creation - will be implemented with test fixtures")

    @pytest.mark.asyncio
    async def test_create_artist_returns_400_for_invalid_name(self, async_client: AsyncClient):
        """
        Test that invalid name returns 400 Bad Request

        Requirements:
        - 1.7: Return 400 for validation errors
        """
        # This will be a unit test style since we need auth
        pytest.skip("Requires admin auth - will test via service layer")

    @pytest.mark.asyncio
    async def test_create_artist_returns_400_for_invalid_country(self, async_client: AsyncClient):
        """
        Test that invalid country code returns 400 Bad Request

        Requirements:
        - 1.8: Return 400 for invalid country code
        """
        pytest.skip("Requires admin auth - will test via service layer")


class TestArtistRetrievalEndpoints:
    """Test artist retrieval endpoints - Task 5.3"""

    @pytest.mark.asyncio
    async def test_get_artist_by_id_allows_guest_access(self, async_client: AsyncClient):
        """
        Test that getting artist by ID allows guest access

        Requirements:
        - 2.8: Allow guest and authenticated users to retrieve
        """
        # Try to access artist endpoint without authentication
        response = await async_client.get("/api/v1/artists/1")

        # Should not return 401 or 403 (even if 404 because artist doesn't exist)
        assert response.status_code != 401, "Should allow guest access"
        assert response.status_code != 403, "Should allow guest access"

    @pytest.mark.asyncio
    async def test_list_artists_allows_guest_access(self, async_client: AsyncClient):
        """
        Test that listing artists allows guest access

        Requirements:
        - 2.8: Allow guest and authenticated users to retrieve
        """
        # Try to list artists without authentication
        response = await async_client.get("/api/v1/artists")

        # Should return 200 (might be empty list)
        assert response.status_code == 200, "Should allow guest access to list"
        assert "items" in response.json() or isinstance(response.json(), list), "Should return list structure"

    @pytest.mark.asyncio
    async def test_get_artist_by_id_returns_404_when_not_found(self, async_client: AsyncClient):
        """
        Test that getting non-existent artist returns 404

        Requirements:
        - 2.6: Return 404 Not Found when artist doesn't exist
        """
        response = await async_client.get("/api/v1/artists/99999")

        assert response.status_code == 404, "Should return 404 for non-existent artist"
        assert "not found" in response.json()["detail"].lower()


class TestArtistSearchEndpoint:
    """Test artist search endpoint - Task 5.4"""

    @pytest.mark.asyncio
    async def test_search_artists_returns_400_for_short_query(self, async_client: AsyncClient):
        """
        Test that short search query returns 400

        Requirements:
        - 3.2: Reject queries less than 2 characters
        """
        response = await async_client.get("/api/v1/artists/search?q=A")

        # FastAPI returns 422 for Pydantic validation errors
        assert response.status_code == 422, "Should return 422 for validation error"
        # Check that error mentions minimum length
        response_data = response.json()
        assert "detail" in response_data, "Response should have detail field"

    @pytest.mark.asyncio
    async def test_search_artists_returns_empty_array_when_no_results(self, async_client: AsyncClient):
        """
        Test that search returns empty array when no results

        Requirements:
        - 3.5: Return 200 OK with empty items array
        """
        response = await async_client.get("/api/v1/artists/search?q=NonExistentArtist12345")

        assert response.status_code == 200, "Should return 200 even with no results"
        data = response.json()
        assert "items" in data, "Response should have items field"
        assert len(data["items"]) == 0, "Items should be empty array"

    @pytest.mark.asyncio
    async def test_search_artists_supports_pagination(self, async_client: AsyncClient):
        """
        Test that search supports pagination parameters

        Requirements:
        - 3.3: Support pagination parameters
        """
        response = await async_client.get("/api/v1/artists/search?q=test&page=1&page_size=10")

        assert response.status_code in [200, 400], "Should handle pagination params"
        if response.status_code == 200:
            data = response.json()
            assert "items" in data, "Response should have items"
            assert "total" in data or "page" in data, "Response should have pagination info"


class TestArtistUpdateEndpoint:
    """Test artist update endpoint - Task 5.5"""

    @pytest.mark.asyncio
    async def test_update_artist_requires_artist_or_admin_role(self, async_client: AsyncClient):
        """
        Test that artist update requires artist or admin role

        Requirements:
        - 4.5: Return 403 for insufficient permissions
        """
        # Register and login as regular user
        register_data = {"email": f"user_update_{id(self)}@test.com", "password": "Test123!@#"}
        await async_client.post("/api/v1/auth/register", json=register_data)

        login_response = await async_client.post("/api/v1/auth/login", json=register_data)
        assert login_response.status_code == 200

        # Try to update artist as regular user (should fail)
        update_data = {"name": "Updated Name"}
        response = await async_client.put("/api/v1/artists/1", json=update_data)

        # Verify
        assert response.status_code == 403, "Regular user should not be able to update artist"

    @pytest.mark.asyncio
    async def test_update_artist_returns_404_for_invalid_id(self, async_client: AsyncClient):
        """
        Test that updating non-existent artist returns 404

        Requirements:
        - 4.6: Return 404 if artist ID does not exist
        """
        # This test requires auth, so we'll skip for now
        pytest.skip("Requires admin auth - will test after auth fixtures")
