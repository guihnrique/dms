"""
Tests for CORS configuration fixes
Tests that frontend origin is allowed and CORS headers are correct
"""
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_cors_allows_frontend_origin():
    """Test that CORS allows requests from frontend URL (port 5173)"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.options(
            "/api/v1/auth/register",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            }
        )

        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
        assert "POST" in response.headers.get("access-control-allow-methods", "")
        assert response.headers.get("access-control-allow-credentials") == "true"


@pytest.mark.asyncio
async def test_cors_rejects_unknown_origin():
    """Test that CORS rejects requests from unknown origins"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.options(
            "/api/v1/auth/register",
            headers={
                "Origin": "http://malicious-site.com",
                "Access-Control-Request-Method": "POST",
            }
        )

        # Should not have CORS headers for unknown origin
        assert response.headers.get("access-control-allow-origin") != "http://malicious-site.com"


@pytest.mark.asyncio
async def test_cors_allows_credentials():
    """Test that CORS configuration allows credentials (cookies)"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.options(
            "/api/v1/auth/login",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
            }
        )

        assert response.headers.get("access-control-allow-credentials") == "true"


@pytest.mark.asyncio
async def test_cors_allows_required_headers():
    """Test that CORS allows required headers (Content-Type, Authorization)"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.options(
            "/api/v1/auth/register",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type,authorization",
            }
        )

        allowed_headers = response.headers.get("access-control-allow-headers", "").lower()
        assert "content-type" in allowed_headers
        assert "authorization" in allowed_headers
