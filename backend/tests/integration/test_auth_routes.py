"""
Integration tests for Authentication Routes - Task 3.2, 3.3
Tests verify complete user registration flow through API endpoints
"""
import pytest
import time
from app.models.user import User


def unique_email(prefix="test"):
    """Generate unique email for testing"""
    return f"{prefix}{int(time.time()*1000)}@example.com"


@pytest.mark.asyncio
async def test_register_user_with_valid_data_returns_201(async_client):
    """
    RED PHASE: Test user registration with valid data
    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
    """
    email = unique_email("newuser")

    payload = {
        "email": email,
        "password": "SecurePass123!"
    }

    response = await async_client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 201
    data = response.json()

    # Verify response includes user data
    assert "id" in data
    assert data["email"] == email
    assert "role" in data
    assert data["role"] == "user"
    assert "created_at" in data

    # Verify password_hash not in response (security)
    assert "password_hash" not in data
    assert "password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email_returns_409(async_client):
    """
    RED PHASE: Test that duplicate email returns 409 Conflict
    Requirements: 1.6
    """
    email = unique_email("duplicate")

    payload = {
        "email": email,
        "password": "SecurePass123!"
    }

    # First registration should succeed
    response1 = await async_client.post("/api/v1/auth/register", json=payload)
    assert response1.status_code == 201

    # Second registration with same email should fail
    response2 = await async_client.post("/api/v1/auth/register", json=payload)
    assert response2.status_code == 409

    data = response2.json()
    assert "detail" in data
    assert "already registered" in data["detail"].lower()


@pytest.mark.asyncio
async def test_register_invalid_email_returns_422(async_client):
    """
    RED PHASE: Test that invalid email format returns 422 Unprocessable Entity
    Requirements: 1.1, 1.7
    """
    invalid_payloads = [
        {"email": "not-an-email", "password": "SecurePass123!"},
        {"email": "@example.com", "password": "SecurePass123!"},
        {"email": "user@", "password": "SecurePass123!"},
    ]

    for payload in invalid_payloads:
        response = await async_client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


@pytest.mark.asyncio
async def test_register_weak_password_returns_422(async_client):
    """
    RED PHASE: Test that weak password returns 422 with detailed error
    Requirements: 1.2, 1.7
    """
    weak_payloads = [
        {"email": "user@example.com", "password": "short"},  # Too short
        {"email": "user@example.com", "password": "nouppercase123!"},  # No uppercase
        {"email": "user@example.com", "password": "NOLOWERCASE123!"},  # No lowercase
        {"email": "user@example.com", "password": "NoDigits!"},  # No digit
        {"email": "user@example.com", "password": "NoSpecial123"},  # No special char
    ]

    for payload in weak_payloads:
        response = await async_client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


@pytest.mark.asyncio
async def test_register_missing_fields_returns_422(async_client):
    """
    RED PHASE: Test that missing required fields returns 422
    Requirements: 1.7
    """
    invalid_payloads = [
        {"email": "user@example.com"},  # Missing password
        {"password": "SecurePass123!"},  # Missing email
        {},  # Missing both
    ]

    for payload in invalid_payloads:
        response = await async_client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_never_stores_plain_password(async_client):
    """
    RED PHASE: Test that plain password is never stored in database
    Requirements: 1.8, 6.4, 6.5

    Note: This test verifies via response. DB verification happens in unit tests.
    """
    email = unique_email("secure")

    payload = {
        "email": email,
        "password": "PlainPassword123!"
    }

    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201

    # Verify password not exposed in response
    data = response.json()
    assert "password" not in data
    assert "password_hash" not in data
    assert payload["password"] not in str(data)


@pytest.mark.asyncio
async def test_register_password_never_exposed_in_response(async_client):
    """
    RED PHASE: Test that password is never exposed in API response
    Requirements: 1.8, 6.5
    """
    email = unique_email("private")

    payload = {
        "email": email,
        "password": "SecretPass123!"
    }

    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201

    data = response.json()
    response_str = response.text

    # Verify password not in response
    assert "password" not in data
    assert "password_hash" not in data
    assert payload["password"] not in response_str


@pytest.mark.asyncio
async def test_register_sets_default_user_role(async_client):
    """
    RED PHASE: Test that new users get default 'user' role
    Requirements: 1.4
    """
    email = unique_email("defaultrole")

    payload = {
        "email": email,
        "password": "SecurePass123!"
    }

    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["role"] == "user"


@pytest.mark.asyncio
async def test_register_returns_user_id_and_timestamps(async_client):
    """
    RED PHASE: Test that response includes user ID and timestamps
    Requirements: 1.5
    """
    email = unique_email("timestamps")

    payload = {
        "email": email,
        "password": "SecurePass123!"
    }

    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert isinstance(data["id"], int)
    assert data["id"] > 0

    assert "created_at" in data
    # Verify timestamp format (ISO 8601)
    from datetime import datetime
    datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
