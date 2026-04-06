-- Migration 007: Create playlist_songs join table
-- Task 1.2: Database schema for playlist-song relationships
-- Requirements: 5 (Add Song), 12 (Duplicate Handling)

-- Create playlist_songs join table
CREATE TABLE playlist_songs (
    id SERIAL PRIMARY KEY,
    playlist_id INTEGER NOT NULL REFERENCES playlists(id) ON DELETE CASCADE,
    song_id INTEGER NOT NULL REFERENCES songs(id) ON DELETE RESTRICT,
    position INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Composite index on (playlist_id, position) for position-based queries and reordering
CREATE INDEX idx_playlist_songs_playlist_position ON playlist_songs(playlist_id, position);

-- Index on song_id for reverse lookups (which playlists contain this song)
CREATE INDEX idx_playlist_songs_song ON playlist_songs(song_id);

-- NO unique constraint on (playlist_id, song_id) to allow duplicate songs
-- This is intentional per Requirement 12: users can add same song multiple times

-- Check constraint: position must be positive
ALTER TABLE playlist_songs ADD CONSTRAINT chk_playlist_songs_position_positive
    CHECK (position > 0);

-- Comments for documentation
COMMENT ON TABLE playlist_songs IS 'Many-to-many relationship between playlists and songs with position ordering';
COMMENT ON COLUMN playlist_songs.id IS 'Surrogate key enables duplicate songs in same playlist';
COMMENT ON COLUMN playlist_songs.playlist_id IS 'FK to playlists (CASCADE delete when playlist deleted)';
COMMENT ON COLUMN playlist_songs.song_id IS 'FK to songs (RESTRICT delete to prevent broken references)';
COMMENT ON COLUMN playlist_songs.position IS 'Song position in playlist (1, 2, 3, ...) for ordering';
COMMENT ON INDEX idx_playlist_songs_playlist_position IS 'Composite index for efficient position queries and reordering';
