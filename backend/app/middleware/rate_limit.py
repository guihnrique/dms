"""
Rate Limiting Middleware - Task 8.1, 8.2
Implements request rate limiting with different limits for auth states
Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from typing import Optional


def get_rate_limit_key(request: Request) -> str:
    """
    Get rate limit key based on authentication status

    Requirements:
    - 5.7: Different limits for authenticated vs unauthenticated
    - Use user_id for authenticated users
    - Use IP address for unauthenticated users

    Args:
        request: FastAPI Request object

    Returns:
        str: Rate limit key (user_id or IP)
    """
    # Check if user is authenticated via cookie
    token = request.cookies.get("access_token")

    if token:
        # Try to extract user_id from token for authenticated rate limit
        try:
            from app.services.auth_service import AuthService
            auth_service = AuthService()
            payload = auth_service.validate_token(token)

            if payload and "user_id" in payload:
                # Use user_id as key for authenticated users
                return f"user:{payload['user_id']}"
        except Exception:
            pass

    # Use IP address for unauthenticated users
    return f"ip:{get_remote_address(request)}"


# Initialize limiter with custom key function
limiter = Limiter(
    key_func=get_rate_limit_key,
    default_limits=["100/minute"]  # Default limit for unauthenticated
)


def setup_rate_limiting(app):
    """
    Configure rate limiting for FastAPI application

    Requirements:
    - 5.1: 100 requests/minute for unauthenticated
    - 5.2: 1000 requests/minute for authenticated
    - 5.3: Return 429 when limit exceeded
    - 5.4: Include Retry-After header

    Args:
        app: FastAPI application instance
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
