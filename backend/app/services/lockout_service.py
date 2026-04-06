"""
Account Lockout Service - Task 15.1, 15.2
Implements account lockout after failed login attempts
Requirements: 13.1, 13.2, 13.3, 13.4, 13.5
"""
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.repositories.user_repository import UserRepository


class LockoutService:
    """
    Service for account lockout management

    Requirements:
    - 13.1: Lock account after 5 failed attempts in 15 minutes
    - 13.2: Lock for 15 minutes
    - 13.3: Reset counter after successful login
    - 13.4: Return clear error message when locked
    - 13.5: Track lockout in audit log
    """

    MAX_ATTEMPTS = 5
    LOCKOUT_WINDOW_MINUTES = 15
    LOCKOUT_DURATION_MINUTES = 15

    def __init__(self, db: AsyncSession):
        """
        Initialize lockout service

        Args:
            db: Database session
        """
        self.db = db
        self.user_repository = UserRepository(db)

    async def increment_failed_attempts(self, user: User) -> User:
        """
        Increment failed login attempts and lock if threshold reached

        Args:
            user: User model instance

        Returns:
            User: Updated user
        """
        user.failed_login_attempts += 1

        # Lock account if threshold reached
        if user.failed_login_attempts >= self.MAX_ATTEMPTS:
            user.account_locked_until = datetime.utcnow() + timedelta(
                minutes=self.LOCKOUT_DURATION_MINUTES
            )

        await self.db.flush()
        await self.db.refresh(user)

        return user

    async def reset_failed_attempts(self, user: User) -> User:
        """
        Reset failed attempts counter after successful login

        Args:
            user: User model instance

        Returns:
            User: Updated user
        """
        user.failed_login_attempts = 0
        user.account_locked_until = None

        await self.db.flush()
        await self.db.refresh(user)

        return user

    def is_locked(self, user: User) -> bool:
        """
        Check if account is currently locked

        Args:
            user: User model instance

        Returns:
            bool: True if account is locked
        """
        return user.is_locked

    def get_lockout_remaining_time(self, user: User) -> int:
        """
        Get remaining lockout time in seconds

        Args:
            user: User model instance

        Returns:
            int: Seconds until unlock (0 if not locked)
        """
        if not user.account_locked_until:
            return 0

        remaining = user.account_locked_until - datetime.utcnow()
        return max(0, int(remaining.total_seconds()))
