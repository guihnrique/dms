"""
User Repository - Data access layer for User model
Task 3.2 - Database operations for user registration
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole


class UserRepository:
    """
    Repository for User model database operations

    Requirements:
    - 1.3: Create user with hashed password
    - 1.4: Set default role
    - 1.6: Check for duplicate emails
    - 9.1: Use ORM for SQL injection prevention
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session

        Args:
            db: Async database session
        """
        self.db = db

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address

        Args:
            email: User email to search for

        Returns:
            User if found, None otherwise
        """
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID

        Args:
            user_id: User ID to search for

        Returns:
            User if found, None otherwise
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_user(
        self,
        email: str,
        password_hash: str,
        role: str = UserRole.USER.value
    ) -> User:
        """
        Create new user in database

        Args:
            email: User email address
            password_hash: Hashed password (bcrypt)
            role: User role (default: 'user')

        Returns:
            Created User object with ID

        Raises:
            Exception: If database operation fails
        """
        user = User(
            email=email,
            password_hash=password_hash,
            role=role
        )

        self.db.add(user)
        await self.db.flush()  # Flush to get ID without committing
        await self.db.refresh(user)  # Refresh to get all fields including defaults

        return user
