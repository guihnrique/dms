"""
Song Model - Task 1.4
SQLAlchemy model for song entity with soft delete
Requirements: 8.1-8.9, 11.1-11.7, 12.1
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.models.user import Base


class Song(Base):
    """
    Song model for music catalog with soft delete support

    Requirements:
    - 8.1: Song creation with validation
    - 8.2: Title validation (1-200 characters)
    - 8.3: Album relationship (album_id foreign key)
    - 8.4: Duration validation (1-7200 seconds)
    - 11.1: Soft delete pattern with deleted_at
    - 11.2: Deleted songs retained in database
    - 12.1: Album → Songs foreign key
    """
    __tablename__ = "songs"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Song attributes
    title = Column(String(200), nullable=False)
    album_id = Column(Integer, ForeignKey("albums.id", ondelete="CASCADE"), nullable=False, index=True)
    duration_seconds = Column(Integer, nullable=False)
    genre = Column(String(100), nullable=True)
    year = Column(Integer, nullable=True)
    external_links = Column(JSONB, nullable=True)

    # Review aggregates (denormalized for performance)
    average_rating = Column(Numeric(2, 1), nullable=True)
    review_count = Column(Integer, nullable=False, default=0, server_default="0")

    # Soft delete
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True, index=True)

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    album = relationship("Album", back_populates="songs")
    reviews = relationship("Review", back_populates="song", cascade="all, delete-orphan")

    @property
    def is_deleted(self) -> bool:
        """Check if song is soft deleted"""
        return self.deleted_at is not None

    def __repr__(self):
        """String representation"""
        status = "deleted" if self.is_deleted else "active"
        return f"<Song(id={self.id}, title='{self.title}', album_id={self.album_id}, status='{status}')>"

    def __str__(self):
        """Human-readable string"""
        duration_min = self.duration_seconds // 60
        duration_sec = self.duration_seconds % 60
        return f"{self.title} ({duration_min}:{duration_sec:02d})"
