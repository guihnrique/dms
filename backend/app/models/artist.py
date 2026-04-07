"""
Artist Model - Task 1.4
SQLAlchemy model for artist entity
Requirements: 1.1-1.8, 12.2
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship
from app.models.user import Base


class Artist(Base):
    """
    Artist model for music catalog

    Requirements:
    - 1.1: Artist creation with validation
    - 1.2: Name validation (1-200 characters)
    - 1.3: Country code validation (ISO 3166-1 alpha-2)
    - 1.4: Timestamps (created_at, updated_at)
    - 12.2: Artist → Albums one-to-many relationship
    """
    __tablename__ = "artists"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Artist attributes
    name = Column(String(200), nullable=False)
    country = Column(String(2), nullable=False)  # ISO 3166-1 alpha-2
    photo_url = Column(String, nullable=True)  # Artist profile photo URL

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    albums = relationship("Album", back_populates="artist", cascade="all, delete")

    def __repr__(self):
        """String representation"""
        return f"<Artist(id={self.id}, name='{self.name}', country='{self.country}')>"

    def __str__(self):
        """Human-readable string"""
        return f"{self.name} ({self.country})"
