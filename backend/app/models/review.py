"""
Review and ReviewVote Models - Task 1.4
SQLAlchemy models for reviews and votes
Requirements: 1, 7
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Review(Base):
    """
    Review model for user reviews on songs

    Requirements:
    - 1: Submit Review with rating and optional body
    - 10: One review per user per song (unique constraint)
    """
    __tablename__ = "reviews"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    song_id = Column(Integer, ForeignKey("songs.id", ondelete="CASCADE"), nullable=False, index=True)

    # Review content
    rating = Column(Integer, nullable=False)
    body = Column(Text, nullable=True)

    # Moderation and engagement
    is_flagged = Column(Boolean, nullable=False, default=False, server_default="false")
    helpful_count = Column(Integer, nullable=False, default=0, server_default="0")

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="reviews")
    song = relationship("Song", back_populates="reviews")
    votes = relationship("ReviewVote", back_populates="review", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
        CheckConstraint('LENGTH(body) <= 2000', name='check_body_length'),
    )

    def __repr__(self):
        """String representation"""
        return f"<Review(id={self.id}, user_id={self.user_id}, song_id={self.song_id}, rating={self.rating})>"


class ReviewVote(Base):
    """
    ReviewVote model for helpfulness voting

    Requirements:
    - 7: Helpfulness Voting (helpful/not_helpful)
    """
    __tablename__ = "review_votes"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    review_id = Column(UUID(as_uuid=True), ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False, index=True)

    # Vote data
    vote_type = Column(String(20), nullable=False)  # "helpful" or "not_helpful"

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="review_votes")
    review = relationship("Review", back_populates="votes")

    # Constraints
    __table_args__ = (
        CheckConstraint("vote_type IN ('helpful', 'not_helpful')", name='check_vote_type'),
    )

    def __repr__(self):
        """String representation"""
        return f"<ReviewVote(id={self.id}, user_id={self.user_id}, review_id={self.review_id}, vote_type='{self.vote_type}')>"
