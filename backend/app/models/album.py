"""
Album Model - Task 1.4
SQLAlchemy model for album entity
Requirements: 5.1-5.9, 12.1, 12.2
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from app.models.user import Base


class Album(Base):
    """
    Album model for music catalog

    Requirements:
    - 5.1: Album creation with validation
    - 5.2: Title validation (1-200 characters)
    - 5.3: Artist relationship (artist_id foreign key)
    - 5.4: Release year validation
    - 12.1: Album → Songs one-to-many relationship
    - 12.2: Artist → Albums foreign key
    """
    __tablename__ = "albums"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Album attributes
    title = Column(String(200), nullable=False)
    artist_id = Column(Integer, ForeignKey("artists.id", ondelete="RESTRICT"), nullable=False, index=True)
    release_year = Column(Integer, nullable=False)
    album_cover_url = Column(Text, nullable=True)
    genre = Column(String(100), nullable=True)

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    artist = relationship("Artist", back_populates="albums")
    songs = relationship("Song", back_populates="album", cascade="all, delete-orphan")

    def __repr__(self):
        """String representation"""
        return f"<Album(id={self.id}, title='{self.title}', artist_id={self.artist_id}, year={self.release_year})>"

    def __str__(self):
        """Human-readable string"""
        return f"{self.title} ({self.release_year})"
