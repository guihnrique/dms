"""
Password Service - Task 2.1, 2.2
Handles password hashing and verification using bcrypt
Requirements: 1.3, 6.1, 6.2, 6.3, 6.4
"""
import bcrypt
from typing import Union


class PasswordService:
    """
    Service for secure password hashing and verification

    Requirements:
    - 1.3: Password hashing during user creation
    - 6.1: Hash passwords with bcrypt algorithm
    - 6.2: Use bcrypt cost factor minimum 12
    - 6.3: Compare passwords using bcrypt.compare
    - 6.4: Never log or expose passwords in plain text
    """

    def __init__(self, cost_factor: int = 12):
        """
        Initialize password service

        Args:
            cost_factor: Bcrypt cost factor (default 12, min 12)
                        Higher = more secure but slower
                        Cost 12 ≈ 250ms hash time
        """
        if cost_factor < 12:
            raise ValueError("Cost factor must be at least 12 for security")

        self.cost_factor = cost_factor

    def hash_password(self, plain_password: str) -> str:
        """
        Hash password using bcrypt with cost factor 12

        Requirements:
        - 6.1: Use bcrypt algorithm with random salt
        - 6.2: Cost factor minimum 12 (~250ms)
        - 6.4: Never expose plain password

        Args:
            plain_password: Plain text password to hash

        Returns:
            Bcrypt hash string (includes salt and cost factor)
            Format: $2b$12$[22-char-salt][31-char-hash]

        Raises:
            ValueError: If password is empty

        Example:
            >>> service = PasswordService()
            >>> hashed = service.hash_password("MyPassword123!")
            >>> print(hashed)
            $2b$12$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy
        """
        if not plain_password:
            raise ValueError("Password cannot be empty")

        # Convert string to bytes (bcrypt requires bytes)
        password_bytes = plain_password.encode('utf-8')

        # Generate salt with specified cost factor and hash
        # bcrypt.gensalt() generates a random salt each time
        # bcrypt.hashpw() combines salt + password and hashes
        salt = bcrypt.gensalt(rounds=self.cost_factor)
        hashed = bcrypt.hashpw(password_bytes, salt)

        # Convert bytes back to string for storage
        return hashed.decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against bcrypt hash

        Requirements:
        - 2.1: Validate credentials during authentication
        - 6.3: Use bcrypt.checkpw for constant-time comparison
        - 6.4: Never expose plain password

        Args:
            plain_password: Plain text password to verify
            hashed_password: Bcrypt hash to compare against

        Returns:
            True if password matches hash, False otherwise

        Note:
            Uses constant-time comparison to prevent timing attacks.
            Both correct and incorrect passwords take similar time.

        Example:
            >>> service = PasswordService()
            >>> hashed = service.hash_password("MyPassword123!")
            >>> service.verify_password("MyPassword123!", hashed)
            True
            >>> service.verify_password("WrongPassword", hashed)
            False
        """
        if not plain_password or not hashed_password:
            return False

        try:
            # Convert strings to bytes
            password_bytes = plain_password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')

            # bcrypt.checkpw performs constant-time comparison
            # Returns True if match, False otherwise
            # Timing-attack resistant: same execution time regardless of result
            return bcrypt.checkpw(password_bytes, hashed_bytes)

        except Exception:
            # If any error occurs (invalid hash format, etc), return False
            # Don't expose error details for security
            return False
