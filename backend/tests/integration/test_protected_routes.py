"""
Integration tests for Protected Routes - Task 6.1, 6.2
Tests verify authentication for protected endpoints
"""
import pytest
import time


def unique_email(prefix="protected"):
    """Generate unique email for testing"""
    return f"{prefix}{int(time.time()*1000)}@example.com"


@pytest.mark.asyncio
async def test_protected_route_requires_authentication(async_client):
    """
    RED PHASE: Test that protected route requires authentication
    Requirements: 4.1, 4.6
    """
    # Try to access protected route without token
    response = await async_client.get("/api/v1/auth/me")

    # Should return 401 Unauthorized
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_protected_route_with_valid_token_returns_user(async_client):
    """
    RED PHASE: Test that valid token grants access to protected route
    Requirements: 4.1, 4.2, 4.3
    """
    email = unique_email("validtoken")
    password = "SecurePass123!"

    # Register and login
    await async_client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login_response = await async_client.post("/api/v1/auth/login", json={"email": email, "password": password})

    # Get token from cookie
    assert "access_token" in login_response.cookies

    # Access protected route (cookie is automatically sent by httpx)
    response = await async_client.get("/api/v1/auth/me")

    # Should return user data
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert data["role"] == "user"
    assert "id" in data


@pytest.mark.asyncio
async def test_protected_route_with_expired_token_returns_401(async_client):
    """
    RED PHASE: Test that expired token is rejected
    Requirements: 4.4, 4.5
    """
    import jwt
    import os
    from datetime import datetime, timedelta

    # Create expired token
    past_time = datetime.utcnow() - timedelta(hours=2)
    expired_payload = {
        "user_id": 1,
        "email": "user@example.com",
        "role": "user",
        "iat": past_time,
        "exp": past_time + timedelta(seconds=1)
    }

    jwt_secret = os.getenv("JWT_SECRET")
    expired_token = jwt.encode(expired_payload, jwt_secret, algorithm="HS256")

    # Set expired token in cookie
    async_client.cookies.set("access_token", expired_token)

    # Try to access protected route
    response = await async_client.get("/api/v1/auth/me")

    # Should return 401
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_with_invalid_signature_returns_401(async_client):
    """
    RED PHASE: Test that invalid signature is rejected
    Requirements: 4.4
    """
    import jwt
    from datetime import datetime, timedelta

    # Create token with wrong secret
    payload = {
        "user_id": 1,
        "email": "user@example.com",
        "role": "user",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=24)
    }

    invalid_token = jwt.encode(payload, "wrong-secret", algorithm="HS256")

    # Set invalid token in cookie
    async_client.cookies.set("access_token", invalid_token)

    # Try to access protected route
    response = await async_client.get("/api/v1/auth/me")

    # Should return 401
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_with_malformed_token_returns_401(async_client):
    """
    GREEN PHASE: Test that malformed token is rejected
    Requirements: 4.4
    """
    # Set malformed token
    async_client.cookies.set("access_token", "not.a.valid.token")

    response = await async_client.get("/api/v1/auth/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_returns_correct_user_data(async_client):
    """
    GREEN PHASE: Test that protected route returns correct user data
    Requirements: 4.3
    """
    email = unique_email("userdata")
    password = "SecurePass123!"

    # Register
    register_response = await async_client.post("/api/v1/auth/register", json={"email": email, "password": password})
    user_id = register_response.json()["id"]

    # Login
    await async_client.post("/api/v1/auth/login", json={"email": email, "password": password})

    # Access protected route
    response = await async_client.get("/api/v1/auth/me")

    assert response.status_code == 200
    data = response.json()

    # Verify all user fields
    assert data["id"] == user_id
    assert data["email"] == email
    assert data["role"] == "user"
    assert "created_at" in data
    assert "password_hash" not in data  # Should never expose password_hash
