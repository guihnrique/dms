"""
Authentication Service - Task 4.1, 4.2
Handles JWT token generation and validation
Requirements: 2.2, 2.3, 2.4, 2.8, 4.2, 4.3, 4.4, 4.5, 4.7
"""
import os
from datetime import datetime, timedelta
from typing import Optional
import jwt
from dotenv import load_dotenv

load_dotenv()


class AuthService:
    """
    Service for JWT token operations

    Requirements:
    - 2.2: Generate JWT tokens for authenticated users
    - 2.3: Include user_id, email, role in token payload
    - 2.4: Set token expiration (24 hours)
    - 2.8: Use HS256 algorithm with JWT_SECRET
    - 4.2-4.7: Token validation with expiration check
    """

    def __init__(self):
        """
        Initialize auth service with JWT configuration
        """
        self.jwt_secret = os.getenv("JWT_SECRET")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_expiration_hours = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

        if not self.jwt_secret:
            raise ValueError("JWT_SECRET environment variable is required")

    def generate_token(self, user_id: int, email: str, role: str) -> str:
        """
        Generate JWT token for authenticated user

        Requirements:
        - 2.2: Create JWT token with user data
        - 2.3: Include user_id, email, role in payload
        - 2.4: Set expiration to 24 hours
        - 2.8: Sign with HS256 algorithm using JWT_SECRET

        Args:
            user_id: User ID
            email: User email address
            role: User role (user, artist, admin)

        Returns:
            str: Signed JWT token

        Example:
            >>> service = AuthService()
            >>> token = service.generate_token(1, "user@example.com", "user")
            >>> print(len(token) > 0)
            True
        """
        # Create payload with user data
        now = datetime.utcnow()
        exp = now + timedelta(hours=self.jwt_expiration_hours)

        payload = {
            "user_id": user_id,
            "email": email,
            "role": role,
            "iat": now,  # Issued at
            "exp": exp   # Expiration
        }

        # Sign token with HS256 algorithm
        token = jwt.encode(
            payload,
            self.jwt_secret,
            algorithm=self.jwt_algorithm
        )

        return token

    def validate_token(self, token: str) -> Optional[dict]:
        """
        Validate JWT token and return payload

        Requirements:
        - 4.2: Validate token signature
        - 4.3: Check token expiration
        - 4.4: Reject invalid signatures
        - 4.5: Reject expired tokens
        - 4.7: Return token payload if valid

        Args:
            token: JWT token string

        Returns:
            dict: Token payload if valid, None if invalid/expired

        Example:
            >>> service = AuthService()
            >>> token = service.generate_token(1, "user@example.com", "user")
            >>> payload = service.validate_token(token)
            >>> payload["user_id"]
            1
        """
        try:
            # Decode and validate token
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm]
            )

            return payload

        except jwt.ExpiredSignatureError:
            # Token has expired
            return None

        except jwt.InvalidTokenError:
            # Invalid token (signature, format, etc.)
            return None

        except Exception:
            # Any other error
            return None
