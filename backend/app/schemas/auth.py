"""
Authentication Schemas - Task 2.3
Pydantic models for authentication request/response validation
Requirements: 1.1, 1.2, 1.7
"""
import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator


class RegisterRequest(BaseModel):
    """
    User registration request schema

    Requirements:
    - 1.1: Validate email format using RFC 5322 standard
    - 1.2: Require password minimum 8 characters with complexity rules
    - 1.7: Return detailed validation errors
    """
    email: EmailStr  # Pydantic EmailStr validates RFC 5322 format
    password: str

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        """
        Validate password strength requirements

        Requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character

        Args:
            value: Password to validate

        Returns:
            Validated password

        Raises:
            ValueError: If password doesn't meet requirements
        """
        errors = []

        # Check minimum length
        if len(value) < 8:
            errors.append("Password must be at least 8 characters")

        # Check for uppercase letter
        if not re.search(r'[A-Z]', value):
            errors.append("Password must contain at least one uppercase letter")

        # Check for lowercase letter
        if not re.search(r'[a-z]', value):
            errors.append("Password must contain at least one lowercase letter")

        # Check for digit
        if not re.search(r'\d', value):
            errors.append("Password must contain at least one digit")

        # Check for special character
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', value):
            errors.append("Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)")

        # If any errors, raise with detailed message
        if errors:
            error_message = "; ".join(errors)
            raise ValueError(error_message)

        return value

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "SecurePassword123!"
                }
            ]
        }
    }


class LoginRequest(BaseModel):
    """
    User login request schema

    Requirements:
    - 2.1: Validate login credentials format
    """
    email: EmailStr
    password: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "SecurePassword123!"
                }
            ]
        }
    }


class UserResponse(BaseModel):
    """
    User response schema (never includes password_hash)

    Requirements:
    - 1.5: Return user details after registration
    - 1.8: Never return password hashes in API responses
    - 6.5: Password hash never exposed
    """
    id: int
    email: str
    role: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,  # Enable SQLAlchemy model conversion
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "email": "user@example.com",
                    "role": "user",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z"
                }
            ]
        }
    }
