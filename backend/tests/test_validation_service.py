"""
Test Validation Service - Task 2.1-2.5
Test-Driven Development (TDD): RED phase

Tests for ValidationService covering country codes, release year, duration, URLs, and text sanitization
Requirements: 1.3, 1.8, 5.4, 5.9, 8.4, 14.1-14.7
"""
import pytest
from datetime import datetime


class TestCountryCodeValidation:
    """Test country code validation - Task 2.1"""

    def test_validate_country_code_accepts_valid_iso_codes(self):
        """
        Test that valid ISO 3166-1 alpha-2 codes are accepted

        Requirements:
        - 1.3: Validate country code (ISO 3166-1 alpha-2)
        - 14.3: Validate against official list
        """
        from app.services.validation_service import ValidationService

        service = ValidationService()

        # Test valid country codes
        assert service.validate_country_code("US") is True, "US should be valid"
        assert service.validate_country_code("GB") is True, "GB should be valid"
        assert service.validate_country_code("BR") is True, "BR should be valid"
        assert service.validate_country_code("JP") is True, "JP should be valid"
        assert service.validate_country_code("DE") is True, "DE should be valid"
        assert service.validate_country_code("FR") is True, "FR should be valid"

    def test_validate_country_code_rejects_invalid_codes(self):
        """
        Test that invalid country codes are rejected

        Requirements:
        - 1.8: Return error for invalid country code
        - 14.3: Validate ISO 3166-1 alpha-2
        """
        from app.services.validation_service import ValidationService

        service = ValidationService()

        # Test invalid codes
        assert service.validate_country_code("XX") is False, "XX should be invalid"
        assert service.validate_country_code("ZZ") is False, "ZZ should be invalid"
        assert service.validate_country_code("ABC") is False, "ABC should be invalid (too long)"
        assert service.validate_country_code("A") is False, "A should be invalid (too short)"
        assert service.validate_country_code("") is False, "Empty string should be invalid"
        assert service.validate_country_code("12") is False, "Numbers should be invalid"

    def test_validate_country_code_case_insensitive(self):
        """
        Test that country code validation is case insensitive

        Requirements:
        - 14.3: Accept uppercase codes
        """
        from app.services.validation_service import ValidationService

        service = ValidationService()

        # Test lowercase codes (should be converted to uppercase)
        assert service.validate_country_code("us") is True, "Lowercase 'us' should be valid"
        assert service.validate_country_code("gb") is True, "Lowercase 'gb' should be valid"
        assert service.validate_country_code("Us") is True, "Mixed case 'Us' should be valid"


class TestReleaseYearValidation:
    """Test release year validation - Task 2.2"""

    def test_validate_release_year_accepts_valid_range(self):
        """
        Test that years in valid range are accepted (1900 to current_year + 1)

        Requirements:
        - 5.4: Validate release year (1900 to current_year + 1)
        - 14.4: Not in future (except current_year + 1 for pre-releases)
        """
        from app.services.validation_service import ValidationService

        service = ValidationService()
        current_year = datetime.now().year

        # Test valid years
        assert service.validate_release_year(1900) is True, "1900 should be valid (minimum)"
        assert service.validate_release_year(1975) is True, "1975 should be valid"
        assert service.validate_release_year(2000) is True, "2000 should be valid"
        assert service.validate_release_year(current_year) is True, "Current year should be valid"
        assert service.validate_release_year(current_year + 1) is True, "Next year should be valid (pre-release)"

    def test_validate_release_year_rejects_future_years(self):
        """
        Test that years beyond current_year + 1 are rejected

        Requirements:
        - 14.4: Reject future years beyond pre-release window
        """
        from app.services.validation_service import ValidationService

        service = ValidationService()
        current_year = datetime.now().year

        # Test invalid future years
        assert service.validate_release_year(current_year + 2) is False, "2 years ahead should be invalid"
        assert service.validate_release_year(current_year + 10) is False, "10 years ahead should be invalid"
        assert service.validate_release_year(3000) is False, "3000 should be invalid"

    def test_validate_release_year_rejects_before_1900(self):
        """
        Test that years before 1900 are rejected

        Requirements:
        - 5.4: Minimum year is 1900
        """
        from app.services.validation_service import ValidationService

        service = ValidationService()

        # Test years before 1900
        assert service.validate_release_year(1899) is False, "1899 should be invalid"
        assert service.validate_release_year(1800) is False, "1800 should be invalid"
        assert service.validate_release_year(0) is False, "0 should be invalid"
        assert service.validate_release_year(-100) is False, "Negative year should be invalid"


class TestDurationValidation:
    """Test duration validation - Task 2.3"""

    def test_validate_duration_accepts_valid_seconds(self):
        """
        Test that durations between 1 and 7200 seconds are accepted

        Requirements:
        - 8.4: Validate duration (1-7200 seconds)
        - 14.5: Realistic song length
        """
        from app.services.validation_service import ValidationService

        service = ValidationService()

        # Test valid durations
        assert service.validate_duration_seconds(1) is True, "1 second should be valid (minimum)"
        assert service.validate_duration_seconds(180) is True, "180 seconds (3 min) should be valid"
        assert service.validate_duration_seconds(300) is True, "300 seconds (5 min) should be valid"
        assert service.validate_duration_seconds(3600) is True, "3600 seconds (1 hour) should be valid"
        assert service.validate_duration_seconds(7200) is True, "7200 seconds (2 hours) should be valid (maximum)"

    def test_validate_duration_rejects_invalid_range(self):
        """
        Test that durations outside 1-7200 range are rejected

        Requirements:
        - 8.4: Duration must be between 1 and 7200 seconds
        - 14.5: Realistic song length constraint
        """
        from app.services.validation_service import ValidationService

        service = ValidationService()

        # Test invalid durations
        assert service.validate_duration_seconds(0) is False, "0 should be invalid"
        assert service.validate_duration_seconds(-1) is False, "Negative duration should be invalid"
        assert service.validate_duration_seconds(7201) is False, "7201 seconds should be invalid (over max)"
        assert service.validate_duration_seconds(10000) is False, "10000 seconds should be invalid"


class TestURLValidation:
    """Test URL validation - Task 2.4"""

    def test_validate_url_accepts_http_https(self):
        """
        Test that valid http/https URLs are accepted

        Requirements:
        - 5.9: Validate album_cover_url format
        - 14.6: Validate URL format using regex
        """
        from app.services.validation_service import ValidationService

        service = ValidationService()

        # Test valid URLs
        assert service.validate_url("http://example.com/image.jpg") is True, "http URL should be valid"
        assert service.validate_url("https://example.com/cover.png") is True, "https URL should be valid"
        assert service.validate_url("https://cdn.example.com/album/cover.jpeg") is True, "Path with folders should be valid"
        assert service.validate_url("https://example.com/image.webp") is True, "webp should be valid"
        assert service.validate_url("https://example.com/image.gif") is True, "gif should be valid"

    def test_validate_url_rejects_javascript_scheme(self):
        """
        Test that javascript: scheme is rejected for security

        Requirements:
        - 14.6: Validate URL format
        - Security: Prevent XSS attacks
        """
        from app.services.validation_service import ValidationService

        service = ValidationService()

        # Test invalid schemes
        assert service.validate_url("javascript:alert('xss')") is False, "javascript: scheme should be invalid"
        assert service.validate_url("data:text/html,<script>alert('xss')</script>") is False, "data: scheme should be invalid"
        assert service.validate_url("ftp://example.com/file.jpg") is False, "ftp: scheme should be invalid"

    def test_validate_url_rejects_invalid_formats(self):
        """
        Test that invalid URL formats are rejected

        Requirements:
        - 14.6: Validate URL format using regex
        """
        from app.services.validation_service import ValidationService

        service = ValidationService()

        # Test invalid formats
        assert service.validate_url("not-a-url") is False, "Plain text should be invalid"
        assert service.validate_url("") is False, "Empty string should be invalid"
        assert service.validate_url("http://") is False, "Incomplete URL should be invalid"


class TestTextSanitization:
    """Test text field sanitization - Task 2.5"""

    def test_sanitize_text_trims_whitespace(self):
        """
        Test that leading/trailing whitespace is trimmed

        Requirements:
        - 14.2: Trim leading and trailing whitespace
        """
        from app.services.validation_service import ValidationService

        service = ValidationService()

        # Test whitespace trimming
        assert service.sanitize_text("  hello  ") == "hello", "Should trim leading/trailing spaces"
        assert service.sanitize_text("\ttext\t") == "text", "Should trim tabs"
        assert service.sanitize_text("\nline\n") == "line", "Should trim newlines"
        assert service.sanitize_text("  multiple   spaces  ") == "multiple   spaces", "Should preserve internal spaces"

    def test_sanitize_text_rejects_empty_strings(self):
        """
        Test that empty or whitespace-only strings raise ValueError

        Requirements:
        - 14.1: Reject empty or whitespace-only strings
        """
        from app.services.validation_service import ValidationService

        service = ValidationService()

        # Test empty strings
        with pytest.raises(ValueError, match="cannot be empty"):
            service.sanitize_text("")

        with pytest.raises(ValueError, match="cannot be empty"):
            service.sanitize_text("   ")

        with pytest.raises(ValueError, match="cannot be empty"):
            service.sanitize_text("\t\n")

    def test_sanitize_text_returns_trimmed_string(self):
        """
        Test that valid text is returned trimmed

        Requirements:
        - 14.2: Trim whitespace from text fields
        """
        from app.services.validation_service import ValidationService

        service = ValidationService()

        # Test normal text
        assert service.sanitize_text("Hello World") == "Hello World", "Normal text should be unchanged"
        assert service.sanitize_text("Test") == "Test", "Single word should be unchanged"
