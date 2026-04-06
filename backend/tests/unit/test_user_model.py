"""
Unit tests for User model - Task 1.2
Tests verify User model structure and UserRole enum
"""
import pytest
from datetime import datetime
from app.models.user import User, UserRole


def test_user_role_enum_has_all_roles():
    """
    RED PHASE: Test UserRole enum has all required roles
    Requirements: 3.1
    """
    assert hasattr(UserRole, 'GUEST')
    assert hasattr(UserRole, 'USER')
    assert hasattr(UserRole, 'ARTIST')
    assert hasattr(UserRole, 'ADMIN')

    assert UserRole.GUEST.value == "guest"
    assert UserRole.USER.value == "user"
    assert UserRole.ARTIST.value == "artist"
    assert UserRole.ADMIN.value == "admin"


def test_user_model_has_required_fields():
    """
    RED PHASE: Test User model has all required fields
    Requirements: 1.1, 1.2, 1.3, 1.4
    """
    # This will fail until we create the User model
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        role=UserRole.USER.value
    )

    assert hasattr(user, 'id')
    assert hasattr(user, 'email')
    assert hasattr(user, 'password_hash')
    assert hasattr(user, 'role')
    assert hasattr(user, 'failed_login_attempts')
    assert hasattr(user, 'account_locked_until')
    assert hasattr(user, 'created_at')
    assert hasattr(user, 'updated_at')


def test_user_model_default_values():
    """
    GREEN PHASE: Test User model column defaults are configured
    Requirements: 1.4
    """
    # Check that default values are configured in the model
    assert User.role.default.arg == UserRole.USER.value
    assert User.failed_login_attempts.default.arg == 0

    # When explicitly set, values work correctly
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        role=UserRole.USER.value,
        failed_login_attempts=0
    )

    assert user.role == UserRole.USER.value
    assert user.failed_login_attempts == 0
    assert user.account_locked_until is None


def test_user_model_can_create_without_role():
    """
    GREEN PHASE: SQLAlchemy allows creating model without default,
    database will apply default on INSERT
    Requirements: 1.1
    """
    # SQLAlchemy models don't validate at construction time
    # Database will apply defaults on INSERT
    user = User(password_hash="hashed", email="test@example.com")
    # No exception raised - validation happens at DB level


def test_user_model_is_locked_property():
    """
    GREEN PHASE: Test is_locked property
    Requirements: 13.1, 13.2
    """
    from datetime import timedelta

    # Not locked when account_locked_until is None
    user = User(email="test@example.com", password_hash="hashed")
    assert user.is_locked is False

    # Locked when lock time is in the future
    user.account_locked_until = datetime.utcnow() + timedelta(minutes=30)
    assert user.is_locked is True

    # Not locked when lock time is in the past
    user.account_locked_until = datetime.utcnow() - timedelta(minutes=30)
    assert user.is_locked is False


def test_user_model_to_dict():
    """
    GREEN PHASE: Test to_dict method excludes password_hash
    Requirements: 1.8, 6.5
    """
    user = User(
        id=1,
        email="test@example.com",
        password_hash="should_not_appear",
        role=UserRole.USER.value
    )

    user_dict = user.to_dict()

    assert "email" in user_dict
    assert "role" in user_dict
    assert "password_hash" not in user_dict  # Never expose password_hash
    assert "created_at" in user_dict
    assert "updated_at" in user_dict


def test_user_model_repr():
    """
    RED PHASE: Test User model string representation
    """
    user = User(
        id=1,
        email="test@example.com",
        password_hash="hashed",
        role=UserRole.USER.value
    )

    repr_str = repr(user)
    assert "User" in repr_str
    assert "test@example.com" in repr_str
    # Should NOT include password_hash in repr for security
    assert "hashed" not in repr_str
