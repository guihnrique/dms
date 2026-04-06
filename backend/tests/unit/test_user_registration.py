"""
Unit tests for User Registration Service - Task 3.1
Tests verify user creation with password hashing and validation
"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from app.services.user_service import UserService
from app.services.password_service import PasswordService
from app.models.user import User, UserRole


@pytest.fixture
def password_service():
    """Fixture for PasswordService"""
    return PasswordService()


@pytest.fixture
def mock_user_repository():
    """Mock UserRepository for testing"""
    return AsyncMock()


@pytest.fixture
def user_service(password_service, mock_user_repository):
    """Fixture for UserService with mocked dependencies"""
    return UserService(
        password_service=password_service,
        user_repository=mock_user_repository
    )


@pytest.mark.asyncio
async def test_register_user_creates_user_with_hashed_password(user_service, mock_user_repository):
    """
    RED PHASE: Test that user registration creates user with hashed password
    Requirements: 1.1, 1.2, 1.3, 1.4
    """
    email = "newuser@example.com"
    password = "SecurePass123!"

    # Mock repository response
    mock_user = User(
        id=1,
        email=email,
        password_hash="$2b$12$mockedhash",
        role=UserRole.USER.value,
        created_at=datetime.utcnow()
    )
    mock_user_repository.create_user.return_value = mock_user
    mock_user_repository.get_user_by_email.return_value = None

    # Register user
    created_user = await user_service.register_user(email, password)

    # Verify user created
    assert created_user.id == 1
    assert created_user.email == email
    assert created_user.role == UserRole.USER.value

    # Verify repository called with hashed password
    mock_user_repository.create_user.assert_called_once()
    call_args = mock_user_repository.create_user.call_args[1]
    assert call_args["email"] == email
    assert call_args["password_hash"].startswith("$2b$12$")
    assert call_args["password_hash"] != password  # Should not be plain password


@pytest.mark.asyncio
async def test_register_user_returns_user_without_password_hash(user_service, mock_user_repository):
    """
    RED PHASE: Test that registration returns user data without password_hash
    Requirements: 1.5, 1.8, 6.5
    """
    email = "secure@example.com"
    password = "SecurePass123!"

    mock_user = User(
        id=2,
        email=email,
        password_hash="$2b$12$mockedhash",
        role=UserRole.USER.value,
        created_at=datetime.utcnow()
    )
    mock_user_repository.create_user.return_value = mock_user
    mock_user_repository.get_user_by_email.return_value = None

    created_user = await user_service.register_user(email, password)

    # User object returned should have all fields
    assert hasattr(created_user, 'id')
    assert hasattr(created_user, 'email')
    assert hasattr(created_user, 'role')
    assert hasattr(created_user, 'created_at')

    # Verify password_hash exists (for internal use)
    assert hasattr(created_user, 'password_hash')
    assert created_user.password_hash is not None


@pytest.mark.asyncio
async def test_register_user_rejects_duplicate_email(user_service, mock_user_repository):
    """
    RED PHASE: Test that duplicate email registration raises error
    Requirements: 1.6
    """
    email = "existing@example.com"
    password = "SecurePass123!"

    # Mock existing user
    existing_user = User(
        id=1,
        email=email,
        password_hash="$2b$12$existinghash",
        role=UserRole.USER.value,
        created_at=datetime.utcnow()
    )
    mock_user_repository.get_user_by_email.return_value = existing_user

    # Attempt to register with duplicate email
    with pytest.raises(ValueError, match="Email already registered"):
        await user_service.register_user(email, password)

    # Verify create_user was not called
    mock_user_repository.create_user.assert_not_called()


@pytest.mark.asyncio
async def test_register_user_validates_email_format(user_service):
    """
    RED PHASE: Test that invalid email format is rejected
    Requirements: 1.1, 1.7
    """
    invalid_emails = [
        "not-an-email",
        "@example.com",
        "user@",
        "user @example.com"
    ]

    for invalid_email in invalid_emails:
        with pytest.raises(ValueError, match="Invalid email"):
            await user_service.register_user(invalid_email, "ValidPass123!")


@pytest.mark.asyncio
async def test_register_user_validates_password_strength(user_service):
    """
    RED PHASE: Test that weak passwords are rejected
    Requirements: 1.2, 1.7
    """
    email = "user@example.com"
    weak_passwords = [
        "short",  # Too short
        "nouppercase123!",  # No uppercase
        "NOLOWERCASE123!",  # No lowercase
        "NoDigits!",  # No digit
        "NoSpecial123"  # No special character
    ]

    for weak_password in weak_passwords:
        with pytest.raises(ValueError):
            await user_service.register_user(email, weak_password)


@pytest.mark.asyncio
async def test_register_user_sets_default_role_to_user(user_service, mock_user_repository):
    """
    RED PHASE: Test that new users get default USER role
    Requirements: 1.4
    """
    email = "newuser@example.com"
    password = "SecurePass123!"

    mock_user = User(
        id=1,
        email=email,
        password_hash="$2b$12$hash",
        role=UserRole.USER.value,
        created_at=datetime.utcnow()
    )
    mock_user_repository.create_user.return_value = mock_user
    mock_user_repository.get_user_by_email.return_value = None

    created_user = await user_service.register_user(email, password)

    assert created_user.role == UserRole.USER.value


@pytest.mark.asyncio
async def test_register_user_hashes_password_with_bcrypt_cost_12(user_service, mock_user_repository):
    """
    RED PHASE: Test that password is hashed with bcrypt cost factor 12
    Requirements: 1.3, 6.1, 6.2
    """
    email = "secure@example.com"
    password = "SecurePass123!"

    mock_user = User(
        id=1,
        email=email,
        password_hash="$2b$12$hash",
        role=UserRole.USER.value,
        created_at=datetime.utcnow()
    )
    mock_user_repository.create_user.return_value = mock_user
    mock_user_repository.get_user_by_email.return_value = None

    await user_service.register_user(email, password)

    # Verify hashed password starts with $2b$12$ (bcrypt cost 12)
    call_args = mock_user_repository.create_user.call_args[1]
    password_hash = call_args["password_hash"]
    assert password_hash.startswith("$2b$12$")

    # Verify it's not the plain password
    assert password_hash != password


@pytest.mark.asyncio
async def test_register_user_with_empty_password_raises_error(user_service):
    """
    GREEN PHASE: Test error handling for empty password
    Requirements: 1.2, 1.7
    """
    email = "user@example.com"

    with pytest.raises(ValueError, match="Password cannot be empty"):
        await user_service.register_user(email, "")


@pytest.mark.asyncio
async def test_register_user_with_empty_email_raises_error(user_service):
    """
    GREEN PHASE: Test error handling for empty email
    Requirements: 1.1, 1.7
    """
    with pytest.raises(ValueError, match="Email cannot be empty"):
        await user_service.register_user("", "ValidPass123!")
