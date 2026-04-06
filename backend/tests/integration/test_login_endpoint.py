"""
Integration tests for Login Endpoint - Task 5.1, 5.2
Tests verify user authentication with JWT tokens
"""
import pytest
import time


def unique_email(prefix="login"):
    """Generate unique email for testing"""
    return f"{prefix}{int(time.time()*1000)}@example.com"


@pytest.mark.asyncio
async def test_login_with_valid_credentials_returns_jwt_cookie(async_client):
    """
    RED PHASE: Test login with valid credentials returns JWT token
    Requirements: 2.1, 2.2, 2.3, 2.4, 2.7
    """
    email = unique_email("valid")
    password = "SecurePass123!"

    # First register the user
    register_payload = {"email": email, "password": password}
    register_response = await async_client.post("/api/v1/auth/register", json=register_payload)
    assert register_response.status_code == 201

    # Now login with the same credentials
    login_payload = {"email": email, "password": password}
    login_response = await async_client.post("/api/v1/auth/login", json=login_payload)

    # Verify successful login
    assert login_response.status_code == 200

    # Verify token in response body
    data = login_response.json()
    assert "access_token" in data
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0

    # Verify token in cookie
    cookies = login_response.cookies
    assert "access_token" in cookies

    # Verify cookie attributes (httpOnly, secure, SameSite)
    # Note: httpOnly is not visible in response, but we test it in unit tests
    cookie_header = login_response.headers.get("set-cookie", "")
    assert "access_token=" in cookie_header
    assert "HttpOnly" in cookie_header
    assert "SameSite=Strict" in cookie_header or "SameSite=strict" in cookie_header


@pytest.mark.asyncio
async def test_login_with_invalid_email_returns_401(async_client):
    """
    RED PHASE: Test login with non-existent email returns 401
    Requirements: 2.5, 2.6
    """
    email = unique_email("nonexistent")
    password = "SomePassword123!"

    login_payload = {"email": email, "password": password}
    response = await async_client.post("/api/v1/auth/login", json=login_payload)

    # Should return 401 Unauthorized
    assert response.status_code == 401

    # Should return generic error message
    data = response.json()
    assert "detail" in data
    assert "invalid credentials" in data["detail"].lower()


@pytest.mark.asyncio
async def test_login_with_invalid_password_returns_401(async_client):
    """
    RED PHASE: Test login with wrong password returns 401
    Requirements: 2.5, 2.6
    """
    email = unique_email("wrongpass")
    correct_password = "CorrectPass123!"
    wrong_password = "WrongPass123!"

    # Register user
    register_payload = {"email": email, "password": correct_password}
    register_response = await async_client.post("/api/v1/auth/register", json=register_payload)
    assert register_response.status_code == 201

    # Try login with wrong password
    login_payload = {"email": email, "password": wrong_password}
    response = await async_client.post("/api/v1/auth/login", json=login_payload)

    # Should return 401 Unauthorized
    assert response.status_code == 401

    # Should return generic error message (no distinction from invalid email)
    data = response.json()
    assert "detail" in data
    assert "invalid credentials" in data["detail"].lower()


@pytest.mark.asyncio
async def test_login_returns_valid_jwt_token(async_client):
    """
    RED PHASE: Test that returned token is valid JWT with user data
    Requirements: 2.2, 2.3, 2.4
    """
    email = unique_email("jwttest")
    password = "SecurePass123!"

    # Register user
    register_payload = {"email": email, "password": password}
    register_response = await async_client.post("/api/v1/auth/register", json=register_payload)
    assert register_response.status_code == 201
    user_id = register_response.json()["id"]

    # Login
    login_payload = {"email": email, "password": password}
    response = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200

    # Decode token to verify payload
    import jwt
    token = response.json()["access_token"]
    payload = jwt.decode(token, options={"verify_signature": False})

    # Verify user data in token
    assert payload["user_id"] == user_id
    assert payload["email"] == email
    assert payload["role"] == "user"
    assert "iat" in payload
    assert "exp" in payload


@pytest.mark.asyncio
async def test_login_with_missing_email_returns_422(async_client):
    """
    GREEN PHASE: Test login with missing email returns validation error
    Requirements: 2.1
    """
    payload = {"password": "SomePassword123!"}
    response = await async_client.post("/api/v1/auth/login", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_with_missing_password_returns_422(async_client):
    """
    GREEN PHASE: Test login with missing password returns validation error
    Requirements: 2.1
    """
    payload = {"email": "test@example.com"}
    response = await async_client.post("/api/v1/auth/login", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_with_invalid_email_format_returns_422(async_client):
    """
    GREEN PHASE: Test login with invalid email format returns validation error
    Requirements: 2.1
    """
    payload = {"email": "not-an-email", "password": "Password123!"}
    response = await async_client.post("/api/v1/auth/login", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_error_message_does_not_distinguish_email_vs_password(async_client):
    """
    GREEN PHASE: Test that error messages don't reveal if email exists
    Requirements: 2.6
    """
    email = unique_email("distinguish")
    password = "CorrectPass123!"

    # Register user
    await async_client.post("/api/v1/auth/register", json={"email": email, "password": password})

    # Try with non-existent email
    response1 = await async_client.post("/api/v1/auth/login", json={
        "email": unique_email("nonexist"),
        "password": "SomePass123!"
    })

    # Try with wrong password
    response2 = await async_client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "WrongPass123!"
    })

    # Both should have same error message
    assert response1.status_code == 401
    assert response2.status_code == 401
    assert response1.json()["detail"] == response2.json()["detail"]
