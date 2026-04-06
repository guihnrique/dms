"""
User model - Task 1.2
SQLAlchemy model for users table with authentication fields
Requirements: 1.1, 1.2, 1.3, 1.4, 3.1
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base


class UserRole(str, Enum):
    """
    User role enumeration
    Requirements: 3.1 - Role-based access control
    """
    GUEST = "guest"
    USER = "user"
    ARTIST = "artist"
    ADMIN = "admin"


class User(Base):
    """
    User model for authentication and authorization

    Requirements:
    - 1.1: User registration with email and password
    - 1.2: Password validation and hashing
    - 1.3: User creation with default role
    - 1.4: Timestamps for user lifecycle
    - 3.1: Role-based access control (RBAC)
    - 13.1: Account lockout for brute force protection
    """
    __tablename__ = "users"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Authentication fields (Requirements: 1.1, 1.2)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # Authorization (Requirements: 3.1)
    role = Column(String(20), nullable=False, default=UserRole.USER.value)

    # Security tracking (Requirements: 13.1)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    account_locked_until = Column(TIMESTAMP(timezone=True), nullable=True)

    # Timestamps (Requirements: 1.4, 4.2, 4.3)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    playlists = relationship("Playlist", back_populates="owner", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    review_votes = relationship("ReviewVote", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        """
        String representation (does NOT include password_hash for security)
        """
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"

    def __str__(self):
        """
        Human-readable string
        """
        return f"User {self.email} ({self.role})"

    @property
    def is_locked(self) -> bool:
        """
        Check if account is currently locked
        Requirements: 13.1, 13.2
        """
        if self.account_locked_until is None:
            return False
        return datetime.utcnow() < self.account_locked_until

    def to_dict(self, include_timestamps: bool = True) -> dict:
        """
        Convert user to dictionary (never includes password_hash)
        Requirements: 1.8, 6.5
        """
        data = {
            "id": self.id,
            "email": self.email,
            "role": self.role,
        }

        if include_timestamps:
            data["created_at"] = self.created_at.isoformat() if self.created_at else None
            data["updated_at"] = self.updated_at.isoformat() if self.updated_at else None

        return data
