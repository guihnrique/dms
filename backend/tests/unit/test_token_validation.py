"""
Unit tests for JWT Token Validation - Task 4.2
Tests verify token validation with expiration checks
"""
import pytest
import time
import jwt
from datetime import datetime, timedelta
from app.services.auth_service import AuthService


@pytest.fixture
def auth_service():
    """Fixture for AuthService"""
    return AuthService()


def test_validate_token_returns_payload_for_valid_token(auth_service):
    """
    RED PHASE: Test that valid token returns payload
    Requirements: 4.2, 4.7
    """
    user_id = 1
    email = "user@example.com"
    role = "user"

    # Generate valid token
    token = auth_service.generate_token(user_id=user_id, email=email, role=role)

    # Validate token
    payload = auth_service.validate_token(token)

    # Verify payload is returned
    assert payload is not None
    assert payload["user_id"] == user_id
    assert payload["email"] == email
    assert payload["role"] == role
    assert "iat" in payload
    assert "exp" in payload


def test_validate_token_rejects_expired_token(auth_service):
    """
    RED PHASE: Test that expired token is rejected
    Requirements: 4.3, 4.5
    """
    import os
    from datetime import datetime, timedelta

    # Create token that's already expired
    past_time = datetime.utcnow() - timedelta(hours=1)
    expired_payload = {
        "user_id": 1,
        "email": "user@example.com",
        "role": "user",
        "iat": past_time,
        "exp": past_time + timedelta(seconds=1)  # Expired 59 minutes ago
    }

    jwt_secret = os.getenv("JWT_SECRET")
    expired_token = jwt.encode(expired_payload, jwt_secret, algorithm="HS256")

    # Validate expired token
    payload = auth_service.validate_token(expired_token)

    # Should return None for expired token
    assert payload is None


def test_validate_token_rejects_invalid_signature(auth_service):
    """
    RED PHASE: Test that token with invalid signature is rejected
    Requirements: 4.4
    """
    user_id = 1
    email = "user@example.com"
    role = "user"

    # Generate token with wrong secret
    wrong_payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=24)
    }

    # Sign with different secret
    invalid_token = jwt.encode(wrong_payload, "wrong-secret-key", algorithm="HS256")

    # Validate token with invalid signature
    payload = auth_service.validate_token(invalid_token)

    # Should return None for invalid signature
    assert payload is None


def test_validate_token_rejects_malformed_token(auth_service):
    """
    RED PHASE: Test that malformed token is rejected
    Requirements: 4.4
    """
    malformed_tokens = [
        "not.a.valid.jwt",
        "invalid-token",
        "",
        "header.payload",  # Missing signature
        "a.b.c.d.e"  # Too many parts
    ]

    for token in malformed_tokens:
        payload = auth_service.validate_token(token)
        assert payload is None, f"Malformed token should be rejected: {token}"


def test_validate_token_rejects_tampered_payload(auth_service):
    """
    GREEN PHASE: Test that token with tampered payload is rejected
    Requirements: 4.4
    """
    user_id = 1
    email = "user@example.com"
    role = "user"

    # Generate valid token
    token = auth_service.generate_token(user_id=user_id, email=email, role=role)

    # Tamper with token (change middle part - payload)
    parts = token.split(".")
    if len(parts) == 3:
        # Modify payload
        parts[1] = parts[1][:-5] + "xxxxx"
        tampered_token = ".".join(parts)

        # Validate tampered token
        payload = auth_service.validate_token(tampered_token)

        # Should return None for tampered token
        assert payload is None


def test_validate_token_handles_none_input(auth_service):
    """
    GREEN PHASE: Test that None input is handled gracefully
    Requirements: 4.4
    """
    payload = auth_service.validate_token(None)
    assert payload is None


def test_validate_token_verifies_algorithm(auth_service):
    """
    GREEN PHASE: Test that only HS256 algorithm is accepted
    Requirements: 2.8, 4.2
    """
    import os

    # Create token with different algorithm (HS512)
    wrong_algo_payload = {
        "user_id": 1,
        "email": "user@example.com",
        "role": "user",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=24)
    }

    jwt_secret = os.getenv("JWT_SECRET")
    wrong_algo_token = jwt.encode(wrong_algo_payload, jwt_secret, algorithm="HS512")

    # Should reject token with wrong algorithm
    payload = auth_service.validate_token(wrong_algo_token)
    assert payload is None


def test_validate_token_checks_all_required_claims(auth_service):
    """
    GREEN PHASE: Test that token validation checks for required claims
    Requirements: 4.7
    """
    # Generate valid token
    token = auth_service.generate_token(1, "user@example.com", "user")
    payload = auth_service.validate_token(token)

    # Verify all required claims are present
    assert "user_id" in payload
    assert "email" in payload
    assert "role" in payload
    assert "iat" in payload
    assert "exp" in payload


def test_validate_token_preserves_payload_values(auth_service):
    """
    GREEN PHASE: Test that validation preserves original payload values
    Requirements: 4.7
    """
    user_id = 42
    email = "specific@example.com"
    role = "admin"

    token = auth_service.generate_token(user_id=user_id, email=email, role=role)
    payload = auth_service.validate_token(token)

    # Verify exact values are preserved
    assert payload["user_id"] == 42
    assert payload["email"] == "specific@example.com"
    assert payload["role"] == "admin"
