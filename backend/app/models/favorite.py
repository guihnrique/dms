"""
Favorite Model - User favorites for songs and albums
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, CheckConstraint, Index
from sqlalchemy.sql import func
from app.database import Base


class Favorite(Base):
    """Favorite entity for user favorites"""
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    song_id = Column(Integer, ForeignKey("songs.id", ondelete="CASCADE"), nullable=True)
    album_id = Column(Integer, ForeignKey("albums.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "(song_id IS NOT NULL AND album_id IS NULL) OR (song_id IS NULL AND album_id IS NOT NULL)",
            name="favorite_type_check"
        ),
        Index("idx_favorites_user_song", "user_id", "song_id", unique=True),
        Index("idx_favorites_user_album", "user_id", "album_id", unique=True),
    )
