"""
Tests for playlist route ordering fix
Tests that /playlists/me works and doesn't conflict with /playlists/{id}
"""
import pytest
from httpx import AsyncClient
from app.main import app


async def create_authenticated_client():
    """Helper to create authenticated client"""
    import time
    client = AsyncClient(app=app, base_url="http://test")

    # Register and login
    register_data = {
        "email": f"playlist_test_{int(time.time())}@example.com",
        "password": "SecurePass123!"
    }
    await client.post("/api/v1/auth/register", json=register_data)
    await client.post("/api/v1/auth/login", json=register_data)

    return client


@pytest.mark.asyncio
async def test_playlists_me_endpoint_works():
    """Test that /playlists/me endpoint works correctly (not parsed as id)"""
    client = await create_authenticated_client()

    try:
        response = await client.get("/playlists/me?page=1&page_size=20")

        # Should return 200, not 422 (which was the bug)
        assert response.status_code == 200

        # Should return playlist list format
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert isinstance(data["items"], list)

    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_playlists_public_endpoint_works():
    """Test that /playlists/public endpoint works correctly"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/playlists/public?page=1&page_size=20")

        # Should return 200
        assert response.status_code == 200

        # Should return playlist list format
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_playlists_id_endpoint_still_works():
    """Test that /playlists/{id} endpoint still works after route reordering"""
    client = await create_authenticated_client()

    try:
        # Create a playlist first
        create_response = await client.post(
            "/playlists",
            json={
                "title": "Test Playlist for ID endpoint",
                "description": "Testing",
                "is_public": True
            }
        )
        assert create_response.status_code == 201
        playlist_id = create_response.json()["id"]

        # Get playlist by ID
        get_response = await client.get(f"/playlists/{playlist_id}")

        assert get_response.status_code == 200
        data = get_response.json()
        assert data["id"] == playlist_id
        assert data["title"] == "Test Playlist for ID endpoint"

    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_playlists_me_does_not_parse_as_integer():
    """Test that 'me' is not parsed as an integer (regression test)"""
    client = await create_authenticated_client()

    try:
        response = await client.get("/playlists/me")

        # Should NOT return 422 Unprocessable Entity
        assert response.status_code != 422

        # If there's an error, it should not be about parsing 'me' as integer
        if response.status_code != 200:
            error = response.json()
            if "detail" in error:
                error_text = str(error["detail"]).lower()
                assert "integer" not in error_text
                assert "parse" not in error_text

    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_route_specificity_order():
    """Test that specific routes (/me, /public) take precedence over /{id}"""
    client = await create_authenticated_client()

    try:
        # Test /me
        me_response = await client.get("/playlists/me")
        assert me_response.status_code == 200
        me_data = me_response.json()
        assert "items" in me_data  # List response

        # Test /public
        public_response = await client.get("/playlists/public")
        assert public_response.status_code == 200
        public_data = public_response.json()
        assert "items" in public_data  # List response

        # Test numeric ID
        id_response = await client.get("/playlists/999999")
        # Should return 404 (not found) or 403 (forbidden), not 422 (validation error)
        assert id_response.status_code in [404, 403]

    finally:
        await client.aclose()
