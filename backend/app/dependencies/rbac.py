"""
Role-Based Access Control Dependencies - Task 7.1
FastAPI dependencies for role verification
Requirements: Role-based authorization
"""
from typing import List
from fastapi import Depends, HTTPException, status
from app.dependencies.auth import get_current_user
from app.models.user import User


def require_role(*allowed_roles: str):
    """
    Dependency factory for role-based access control

    Creates a FastAPI dependency that checks if user has required role.

    Args:
        *allowed_roles: Variable number of allowed role strings

    Returns:
        Dependency function that verifies user role

    Raises:
        HTTPException 403: If user doesn't have required role

    Usage:
        @router.post("/admin-only")
        async def admin_route(user: User = Depends(require_role("admin"))):
            return {"message": "Admin access granted"}

        @router.get("/artist-or-admin")
        async def special_route(user: User = Depends(require_role("artist", "admin"))):
            return {"message": "Special access granted"}
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        """
        Verify that current user has one of the allowed roles

        Args:
            current_user: User from get_current_user dependency

        Returns:
            User: Current user if role check passes

        Raises:
            HTTPException 403: If user role not in allowed_roles
        """
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join(allowed_roles)}"
            )

        return current_user

    return role_checker
