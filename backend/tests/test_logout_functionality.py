"""
Tests for logout functionality
Tests that logout endpoint clears authentication cookie
"""
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_logout_endpoint_exists():
    """Test that logout endpoint exists and returns 200"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/auth/logout")
        assert response.status_code == 200
        assert "message" in response.json()
        assert "logged out" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_logout_clears_authentication_cookie():
    """Test that logout clears the access_token cookie"""
    async with AsyncClient(app=app, base_url="http://test", follow_redirects=True) as client:
        # First register a user
        import time
        register_data = {
            "email": f"logout_test_{int(time.time())}@example.com",
            "password": "SecurePass123!"
        }
        register_response = await client.post("/api/v1/auth/register", json=register_data)
        assert register_response.status_code == 201

        # Login to get authentication cookie
        login_response = await client.post(
            "/api/v1/auth/login",
            json=register_data
        )
        assert login_response.status_code == 200

        # Extract cookie from login response
        cookies = login_response.cookies
        assert "access_token" in cookies

        # Verify we can access protected route with cookie
        me_response = await client.get("/api/v1/auth/me")
        assert me_response.status_code == 200

        # Logout
        logout_response = await client.post("/api/v1/auth/logout")
        assert logout_response.status_code == 200

        # Verify cookie was cleared (Set-Cookie header should set max-age=0 or similar)
        set_cookie = logout_response.headers.get("set-cookie", "")
        assert "access_token" in set_cookie.lower()

        # Verify we can no longer access protected route after logout
        # Note: AsyncClient maintains cookies across requests
        me_response_after = await client.get("/api/v1/auth/me")
        assert me_response_after.status_code == 401


@pytest.mark.asyncio
async def test_logout_works_without_authentication():
    """Test that logout works even if user is not authenticated"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Logout without being logged in
        response = await client.post("/api/v1/auth/logout")

        # Should still return 200 (idempotent operation)
        assert response.status_code == 200
        assert "message" in response.json()


@pytest.mark.asyncio
async def test_logout_response_format():
    """Test that logout returns correct response format"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/auth/logout")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "message" in data
        assert isinstance(data["message"], str)
        assert len(data["message"]) > 0
