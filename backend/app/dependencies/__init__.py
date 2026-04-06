"""
FastAPI Dependencies for authentication and authorization
"""
from app.dependencies.auth import get_current_user
from app.dependencies.rbac import require_role
from app.dependencies.playlist import verify_playlist_ownership

__all__ = ["get_current_user", "require_role", "verify_playlist_ownership"]
