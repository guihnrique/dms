"""
Authentication Dependencies - Task 6.1, 6.2
FastAPI dependencies for protected routes
Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6
"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.models.user import User


async def get_current_user_optional(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Optional authentication dependency for guest-friendly routes

    Returns:
        User if authenticated, None if guest

    Does NOT raise exceptions for missing/invalid tokens
    """
    token: Optional[str] = request.cookies.get("access_token")

    if not token:
        return None

    try:
        # Validate token
        auth_service = AuthService()
        payload = auth_service.verify_token(token)
        user_id = payload.get("user_id")

        if not user_id:
            return None

        # Get user
        user_repo = UserRepository(db)
        user = await user_repo.get_by_id(user_id)

        return user
    except Exception:
        # Suppress all exceptions and return None for guests
        return None


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    FastAPI dependency to extract and validate current user from JWT token

    Requirements:
    - 4.1: Extract JWT token from cookie
    - 4.2: Validate token signature
    - 4.3: Check token expiration
    - 4.4: Reject invalid signatures
    - 4.5: Reject expired tokens
    - 4.6: Return 401 for missing/invalid tokens

    Args:
        request: FastAPI Request object (contains cookies)
        db: Database session

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException 401: If token is missing, invalid, expired, or user not found

    Usage:
        @router.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"user": current_user.email}
    """
    # Extract token from cookie
    token: Optional[str] = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Validate token
    auth_service = AuthService()
    payload = auth_service.validate_token(token)

    if payload is None:
        # Token is invalid or expired
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Extract user_id from payload
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Get user from database
    user_repository = UserRepository(db)
    user = await user_repository.get_user_by_id(user_id)

    if user is None:
        # User was deleted after token was issued
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user
