"""
Unit tests for AuthService - Task 4.1, 4.2
Tests verify JWT token generation and validation
"""
import pytest
import time
from datetime import datetime, timedelta
from app.services.auth_service import AuthService


@pytest.fixture
def auth_service():
    """Fixture for AuthService"""
    return AuthService()


def test_generate_token_includes_user_data(auth_service):
    """
    RED PHASE: Test that JWT token includes user data in payload
    Requirements: 2.2, 2.3, 2.4, 2.8
    """
    user_id = 1
    email = "user@example.com"
    role = "user"

    # Generate token
    token = auth_service.generate_token(user_id=user_id, email=email, role=role)

    # Verify token is a string
    assert isinstance(token, str)
    assert len(token) > 0

    # Decode token to verify payload (without validation for now)
    import jwt
    payload = jwt.decode(token, options={"verify_signature": False})

    # Verify user data in payload
    assert payload["user_id"] == user_id
    assert payload["email"] == email
    assert payload["role"] == role


def test_generate_token_sets_24_hour_expiration(auth_service):
    """
    RED PHASE: Test that token expires in 24 hours
    Requirements: 2.4
    """
    user_id = 1
    email = "user@example.com"
    role = "user"

    # Generate token
    before_time = datetime.utcnow()
    token = auth_service.generate_token(user_id=user_id, email=email, role=role)
    after_time = datetime.utcnow()

    # Decode token to check expiration
    import jwt
    payload = jwt.decode(token, options={"verify_signature": False})

    # Verify 'exp' claim exists
    assert "exp" in payload

    # Verify expiration is ~24 hours from now
    exp_time = datetime.utcfromtimestamp(payload["exp"])
    expected_exp = before_time + timedelta(hours=24)

    # Allow 5 second tolerance for test execution time
    time_diff = abs((exp_time - expected_exp).total_seconds())
    assert time_diff < 5, f"Expiration time difference too large: {time_diff}s"


def test_generate_token_signs_with_hs256(auth_service):
    """
    RED PHASE: Test that token is signed with HS256 algorithm
    Requirements: 2.8
    """
    user_id = 1
    email = "user@example.com"
    role = "user"

    # Generate token
    token = auth_service.generate_token(user_id=user_id, email=email, role=role)

    # Decode header to check algorithm
    import jwt
    header = jwt.get_unverified_header(token)

    assert header["alg"] == "HS256"
    assert header["typ"] == "JWT"


def test_generate_token_uses_jwt_secret_from_env(auth_service):
    """
    RED PHASE: Test that token is signed with JWT_SECRET from environment
    Requirements: 2.8
    """
    import os
    user_id = 1
    email = "user@example.com"
    role = "user"

    # Generate token
    token = auth_service.generate_token(user_id=user_id, email=email, role=role)

    # Get JWT_SECRET from environment
    jwt_secret = os.getenv("JWT_SECRET")
    assert jwt_secret is not None, "JWT_SECRET not set in environment"

    # Verify token can be decoded with the secret
    import jwt
    payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])

    assert payload["user_id"] == user_id
    assert payload["email"] == email


def test_generate_token_creates_unique_tokens(auth_service):
    """
    GREEN PHASE: Test that each token generation creates unique token
    Requirements: 2.3
    """
    user_id = 1
    email = "user@example.com"
    role = "user"

    # Generate two tokens with same data
    token1 = auth_service.generate_token(user_id=user_id, email=email, role=role)
    time.sleep(1.1)  # Wait over 1 second to ensure different timestamps
    token2 = auth_service.generate_token(user_id=user_id, email=email, role=role)

    # Tokens should be different due to different 'iat' (issued at) timestamps
    assert token1 != token2


def test_generate_token_with_different_roles(auth_service):
    """
    GREEN PHASE: Test token generation with different user roles
    Requirements: 2.3
    """
    roles = ["user", "artist", "admin"]

    for role in roles:
        token = auth_service.generate_token(user_id=1, email="test@example.com", role=role)

        import jwt
        payload = jwt.decode(token, options={"verify_signature": False})
        assert payload["role"] == role


def test_generate_token_includes_issued_at_claim(auth_service):
    """
    GREEN PHASE: Test that token includes 'iat' (issued at) claim
    Requirements: 2.3
    """
    token = auth_service.generate_token(user_id=1, email="test@example.com", role="user")

    import jwt
    payload = jwt.decode(token, options={"verify_signature": False})

    # Verify 'iat' claim exists
    assert "iat" in payload

    # Verify 'iat' is close to current time
    iat_time = datetime.utcfromtimestamp(payload["iat"])
    current_time = datetime.utcnow()
    time_diff = abs((current_time - iat_time).total_seconds())

    assert time_diff < 2, f"Issued at time difference too large: {time_diff}s"
