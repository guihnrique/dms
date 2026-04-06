"""
Playlist and PlaylistSong Models - Task 1.3
SQLAlchemy models for user playlists and playlist-song relationships
Requirements: 1, 4, 5, 12
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Playlist(Base):
    """
    Playlist model representing user-created music collections

    Relationships:
    - owner: User who created the playlist (many-to-one)
    - playlist_songs: Songs in this playlist (one-to-many)

    Constraints:
    - title: 1-200 characters
    - owner_user_id: Foreign key to users (CASCADE delete)
    - is_public: Default FALSE (private)
    """
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    owner_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    is_public = Column(Boolean, nullable=False, default=False, server_default="false")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    owner = relationship("User", back_populates="playlists")
    playlist_songs = relationship(
        "PlaylistSong",
        back_populates="playlist",
        cascade="all, delete-orphan",  # CASCADE delete playlist_songs
        lazy="selectin"  # Eager load for performance
    )

    def __repr__(self):
        """String representation for debugging"""
        return f"<Playlist(id={self.id}, title='{self.title}', owner_id={self.owner_user_id}, public={self.is_public})>"


class PlaylistSong(Base):
    """
    PlaylistSong join table for many-to-many relationship with position ordering

    Relationships:
    - playlist: Parent playlist (many-to-one)
    - song: Referenced song (many-to-one)

    Constraints:
    - Surrogate key (id) enables duplicate songs in same playlist (Requirement 12)
    - position: Must be positive integer
    - CASCADE delete when playlist deleted
    - RESTRICT delete when song deleted (prevent broken references)
    """
    __tablename__ = "playlist_songs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    playlist_id = Column(
        Integer,
        ForeignKey("playlists.id", ondelete="CASCADE"),
        nullable=False
    )
    song_id = Column(
        Integer,
        ForeignKey("songs.id", ondelete="RESTRICT"),
        nullable=False
    )
    position = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Check constraint: position must be positive
    __table_args__ = (
        CheckConstraint("position > 0", name="chk_playlist_songs_position_positive"),
    )

    # Relationships
    playlist = relationship("Playlist", back_populates="playlist_songs")
    song = relationship("Song")

    def __repr__(self):
        """String representation for debugging"""
        return f"<PlaylistSong(id={self.id}, playlist_id={self.playlist_id}, song_id={self.song_id}, position={self.position})>"
