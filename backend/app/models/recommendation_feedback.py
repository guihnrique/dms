"""
RecommendationFeedback Model - Task 3.5
Requirements: 11
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.sql import func
from app.database import Base


class RecommendationFeedback(Base):
    """User feedback on recommendations"""
    __tablename__ = "recommendation_feedback"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    song_id = Column(Integer, ForeignKey("songs.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(50), nullable=False)  # accepted, dismissed, clicked
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'song_id'),
    )
