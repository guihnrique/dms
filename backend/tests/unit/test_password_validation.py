"""
Unit tests for Password Strength Validation - Task 2.3
Tests verify Pydantic validators for password requirements
"""
import pytest
from pydantic import ValidationError
from app.schemas.auth import RegisterRequest


def test_validate_password_strength_accepts_strong_password():
    """
    RED PHASE: Test that strong passwords are accepted
    Requirements: 1.2
    """
    # Valid password: 8+ chars, uppercase, lowercase, digit, special
    valid_data = {
        "email": "test@example.com",
        "password": "SecurePass123!"
    }

    request = RegisterRequest(**valid_data)
    assert request.password == "SecurePass123!"


def test_validate_password_rejects_too_short():
    """
    RED PHASE: Test minimum 8 characters requirement
    Requirements: 1.2, 1.7
    """
    invalid_data = {
        "email": "test@example.com",
        "password": "Short1!"  # Only 7 characters
    }

    with pytest.raises(ValidationError) as exc_info:
        RegisterRequest(**invalid_data)

    error = exc_info.value.errors()[0]
    assert "8 characters" in error["msg"].lower()


def test_validate_password_rejects_missing_uppercase():
    """
    RED PHASE: Test uppercase letter requirement
    Requirements: 1.2, 1.7
    """
    invalid_data = {
        "email": "test@example.com",
        "password": "lowercase123!"  # No uppercase
    }

    with pytest.raises(ValidationError) as exc_info:
        RegisterRequest(**invalid_data)

    error = exc_info.value.errors()[0]
    assert "uppercase" in error["msg"].lower()


def test_validate_password_rejects_missing_lowercase():
    """
    RED PHASE: Test lowercase letter requirement
    Requirements: 1.2, 1.7
    """
    invalid_data = {
        "email": "test@example.com",
        "password": "UPPERCASE123!"  # No lowercase
    }

    with pytest.raises(ValidationError) as exc_info:
        RegisterRequest(**invalid_data)

    error = exc_info.value.errors()[0]
    assert "lowercase" in error["msg"].lower()


def test_validate_password_rejects_missing_digit():
    """
    RED PHASE: Test digit requirement
    Requirements: 1.2, 1.7
    """
    invalid_data = {
        "email": "test@example.com",
        "password": "NoDigitPass!"  # No digit
    }

    with pytest.raises(ValidationError) as exc_info:
        RegisterRequest(**invalid_data)

    error = exc_info.value.errors()[0]
    assert "digit" in error["msg"].lower() or "number" in error["msg"].lower()


def test_validate_password_rejects_missing_special_character():
    """
    RED PHASE: Test special character requirement
    Requirements: 1.2, 1.7
    """
    invalid_data = {
        "email": "test@example.com",
        "password": "NoSpecial123"  # No special character
    }

    with pytest.raises(ValidationError) as exc_info:
        RegisterRequest(**invalid_data)

    error = exc_info.value.errors()[0]
    assert "special" in error["msg"].lower()


def test_validate_password_provides_detailed_errors():
    """
    RED PHASE: Test detailed validation error messages
    Requirements: 1.7
    """
    # Multiple violations
    invalid_data = {
        "email": "test@example.com",
        "password": "weak"  # Too short, no uppercase, no digit, no special
    }

    with pytest.raises(ValidationError) as exc_info:
        RegisterRequest(**invalid_data)

    # Should provide detailed error message
    error_msg = str(exc_info.value)
    assert len(error_msg) > 20, "Error message should be detailed"


def test_validate_password_various_special_characters():
    """
    GREEN PHASE: Test various special characters are accepted
    Requirements: 1.2
    """
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    for char in special_chars:
        valid_data = {
            "email": "test@example.com",
            "password": f"Valid123{char}"
        }
        request = RegisterRequest(**valid_data)
        assert request.password == f"Valid123{char}"


def test_validate_email_format():
    """
    GREEN PHASE: Test email validation
    Requirements: 1.1
    """
    # Valid email
    valid_data = {
        "email": "user@example.com",
        "password": "ValidPass123!"
    }
    request = RegisterRequest(**valid_data)
    assert request.email == "user@example.com"

    # Invalid email
    invalid_data = {
        "email": "not-an-email",
        "password": "ValidPass123!"
    }

    with pytest.raises(ValidationError) as exc_info:
        RegisterRequest(**invalid_data)

    assert "email" in str(exc_info.value).lower()


def test_register_request_to_dict():
    """
    GREEN PHASE: Test that RegisterRequest can be serialized
    """
    data = {
        "email": "test@example.com",
        "password": "SecurePass123!"
    }

    request = RegisterRequest(**data)
    request_dict = request.model_dump()

    assert request_dict["email"] == "test@example.com"
    # Password should be included in dict (for processing)
    assert request_dict["password"] == "SecurePass123!"
