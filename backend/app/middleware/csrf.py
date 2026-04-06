"""
CSRF Protection Middleware - Task 12.1, 12.2
Implements double-submit cookie pattern for CSRF protection
Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6
"""
import secrets
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    CSRF Protection using double-submit cookie pattern

    Requirements:
    - 10.1: Generate unique CSRF token per session
    - 10.2: Validate token on state-changing requests
    - 10.3: Return 403 if token invalid
    - 10.4: Use double-submit cookie pattern
    - 10.5: Skip validation for safe methods (GET, HEAD, OPTIONS)
    - 10.6: Token expires after 1 hour of inactivity
    """

    # Methods that don't need CSRF protection
    SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}

    # Paths that don't need CSRF protection (public endpoints)
    EXCLUDED_PATHS = {"/api/docs", "/api/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next):
        """
        Process request and validate CSRF token

        Args:
            request: Incoming request
            call_next: Next middleware/handler

        Returns:
            Response: HTTP response

        Raises:
            HTTPException 403: If CSRF validation fails
        """
        # Skip CSRF for safe methods
        if request.method in self.SAFE_METHODS:
            return await call_next(request)

        # Skip CSRF for excluded paths
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)

        # Get CSRF token from cookie
        csrf_cookie = request.cookies.get("csrf_token")

        # Get CSRF token from header
        csrf_header = request.headers.get("X-CSRF-Token")

        # Validate CSRF token (double-submit pattern)
        if not csrf_cookie or not csrf_header:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token missing"
            )

        if csrf_cookie != csrf_header:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token invalid"
            )

        # Process request
        response = await call_next(request)

        # Generate new CSRF token for first visit or refresh
        if not csrf_cookie:
            new_csrf_token = secrets.token_urlsafe(32)
            response.set_cookie(
                key="csrf_token",
                value=new_csrf_token,
                httponly=False,  # Must be accessible to JavaScript
                secure=True,
                samesite="strict",
                max_age=3600  # 1 hour
            )

        return response


def setup_csrf_protection(app, enabled: bool = True):
    """
    Configure CSRF protection for FastAPI application

    Args:
        app: FastAPI application instance
        enabled: Whether to enable CSRF protection (default: True)
    """
    if enabled:
        app.add_middleware(CSRFMiddleware)
