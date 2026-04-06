"""
User Service - Task 3.1
Handles user registration with password hashing and validation
Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8
"""
import re
from typing import Optional
from app.models.user import User, UserRole
from app.services.password_service import PasswordService


class UserService:
    """
    Service for user management operations

    Requirements:
    - 1.1: Validate email format
    - 1.2: Validate password strength
    - 1.3: Hash passwords before storage
    - 1.4: Set default user role
    - 1.5: Return user details after registration
    - 1.6: Check for duplicate emails
    - 1.7: Provide detailed validation errors
    - 1.8: Never return password hashes
    """

    def __init__(self, password_service: PasswordService, user_repository):
        """
        Initialize user service

        Args:
            password_service: Service for password hashing/verification
            user_repository: Repository for user data persistence
        """
        self.password_service = password_service
        self.user_repository = user_repository

    async def register_user(self, email: str, password: str) -> User:
        """
        Register a new user with email and password

        Requirements:
        - 1.1: Validate email format (RFC 5322)
        - 1.2: Validate password strength (min 8 chars, complexity)
        - 1.3: Hash password with bcrypt cost factor 12
        - 1.4: Set default role to 'user'
        - 1.5: Return user details (id, email, role, timestamps)
        - 1.6: Reject duplicate email registrations
        - 1.7: Return detailed validation errors
        - 1.8: Never expose password_hash in response

        Args:
            email: User email address
            password: Plain text password

        Returns:
            User: Created user object with all fields

        Raises:
            ValueError: If validation fails or email already exists

        Example:
            >>> service = UserService(password_service, repository)
            >>> user = await service.register_user("user@example.com", "SecurePass123!")
            >>> print(user.email)
            user@example.com
        """
        # Validate email first (format check includes empty check)
        if not email:
            raise ValueError("Email cannot be empty")

        email = email.strip()
        if not email:
            raise ValueError("Email cannot be empty")

        # Validate email format (basic RFC 5322 pattern)
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")

        # Validate password is not empty
        if not password or password == "":
            raise ValueError("Password cannot be empty")

        # Validate password strength (same rules as Pydantic validator)
        self._validate_password_strength(password)

        # Check for duplicate email
        existing_user = await self.user_repository.get_user_by_email(email)
        if existing_user is not None:
            raise ValueError("Email already registered")

        # Hash password using bcrypt with cost factor 12
        password_hash = self.password_service.hash_password(password)

        # Create user with default role
        user = await self.user_repository.create_user(
            email=email,
            password_hash=password_hash,
            role=UserRole.USER.value
        )

        return user

    def _validate_password_strength(self, password: str) -> None:
        """
        Validate password strength requirements

        Requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character

        Args:
            password: Password to validate

        Raises:
            ValueError: If password doesn't meet requirements
        """
        errors = []

        # Check minimum length
        if len(password) < 8:
            errors.append("Password must be at least 8 characters")

        # Check for uppercase letter
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")

        # Check for lowercase letter
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")

        # Check for digit
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")

        # Check for special character
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            errors.append("Password must contain at least one special character")

        # If any errors, raise with detailed message
        if errors:
            error_message = "; ".join(errors)
            raise ValueError(error_message)
