"""
Validation Service - Task 2.1-2.5
Centralized validation logic for catalog entities
Requirements: 1.3, 1.8, 5.4, 5.9, 8.4, 14.1-14.7
"""
import re
import pycountry
from datetime import datetime
from typing import Optional


class ValidationService:
    """
    Centralize validation logic for catalog entities

    Requirements:
    - 14.1: Reject empty or whitespace-only strings
    - 14.2: Trim leading and trailing whitespace
    - 14.3: Validate ISO 3166-1 alpha-2 country codes
    - 14.4: Validate release years (1900 to current_year + 1)
    - 14.5: Validate durations (1-7200 seconds)
    - 14.6: Validate URL format (http/https schemes)
    - 14.7: Return detailed validation errors
    """

    def validate_country_code(self, code: str) -> bool:
        """
        Validate ISO 3166-1 alpha-2 country code

        Requirements:
        - 1.3: Validate country code (ISO 3166-1 alpha-2)
        - 14.3: Validate against official ISO data

        Args:
            code: 2-character country code

        Returns:
            bool: True if valid country code, False otherwise

        Examples:
            >>> service = ValidationService()
            >>> service.validate_country_code("US")
            True
            >>> service.validate_country_code("XX")
            False
        """
        if not code or not isinstance(code, str):
            return False

        # Convert to uppercase for case-insensitive validation
        code = code.upper()

        # Check length (must be exactly 2 characters)
        if len(code) != 2:
            return False

        # Check if code exists in pycountry official data
        try:
            country = pycountry.countries.get(alpha_2=code)
            return country is not None
        except (KeyError, LookupError):
            return False

    def validate_release_year(self, year: int) -> bool:
        """
        Validate release year range (1900 to current_year + 1)

        Requirements:
        - 5.4: Validate release year between 1900 and current_year + 1
        - 14.4: Allow pre-release albums (current_year + 1)

        Args:
            year: Release year to validate

        Returns:
            bool: True if valid year, False otherwise

        Examples:
            >>> service = ValidationService()
            >>> service.validate_release_year(1975)
            True
            >>> service.validate_release_year(1800)
            False
        """
        if not isinstance(year, int):
            return False

        current_year = datetime.now().year

        # Allow 1900 to current_year + 1 (for pre-releases)
        return 1900 <= year <= current_year + 1

    def validate_duration_seconds(self, duration: int) -> bool:
        """
        Validate song duration in seconds (1-7200)

        Requirements:
        - 8.4: Validate duration between 1 and 7200 seconds (2 hours)
        - 14.5: Realistic song length constraint

        Args:
            duration: Duration in seconds

        Returns:
            bool: True if valid duration, False otherwise

        Examples:
            >>> service = ValidationService()
            >>> service.validate_duration_seconds(180)
            True
            >>> service.validate_duration_seconds(0)
            False
        """
        if not isinstance(duration, int):
            return False

        # Max duration: 2 hours (7200 seconds)
        return 1 <= duration <= 7200

    def validate_url(self, url: str) -> bool:
        """
        Validate URL format (http/https schemes only)

        Requirements:
        - 5.9: Validate album_cover_url format
        - 14.6: Validate URL format using regex
        - Security: Only allow http/https schemes

        Args:
            url: URL to validate

        Returns:
            bool: True if valid URL, False otherwise

        Examples:
            >>> service = ValidationService()
            >>> service.validate_url("https://example.com/cover.jpg")
            True
            >>> service.validate_url("javascript:alert('xss')")
            False
        """
        if not url or not isinstance(url, str):
            return False

        # Only allow http/https schemes with image extensions
        # Pattern matches:
        # - http:// or https://
        # - Any domain/path
        # - Common image extensions: jpg, jpeg, png, gif, webp
        pattern = r'^https?://[^\s]+\.(jpg|jpeg|png|gif|webp)(\?[^\s]*)?$'

        return re.match(pattern, url, re.IGNORECASE) is not None

    def sanitize_text(self, text: str) -> str:
        """
        Sanitize text field by trimming whitespace and rejecting empty strings

        Requirements:
        - 14.1: Reject empty or whitespace-only strings
        - 14.2: Trim leading and trailing whitespace

        Args:
            text: Text to sanitize

        Returns:
            str: Trimmed text

        Raises:
            ValueError: If text is empty or whitespace-only

        Examples:
            >>> service = ValidationService()
            >>> service.sanitize_text("  hello  ")
            'hello'
            >>> service.sanitize_text("   ")
            Traceback (most recent call last):
                ...
            ValueError: Text cannot be empty or whitespace-only
        """
        if not isinstance(text, str):
            raise ValueError("Text must be a string")

        # Trim leading and trailing whitespace
        trimmed = text.strip()

        # Reject empty or whitespace-only strings
        if not trimmed:
            raise ValueError("Text cannot be empty or whitespace-only")

        return trimmed
