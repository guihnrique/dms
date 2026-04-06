-- Migration 006: Create playlists table
-- Task 1.1: Database schema for user playlists
-- Requirements: 1 (Playlist Creation), 8 (Privacy Control)

-- Create playlists table
CREATE TABLE playlists (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    owner_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index on owner_user_id for querying user's playlists
CREATE INDEX idx_playlists_owner ON playlists(owner_user_id);

-- Partial index on is_public for public playlist queries (only index TRUE values)
CREATE INDEX idx_playlists_public ON playlists(is_public) WHERE is_public = TRUE;

-- Trigger for automatic updated_at timestamp updates
CREATE OR REPLACE FUNCTION update_playlist_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_playlist_updated_at
BEFORE UPDATE ON playlists
FOR EACH ROW
EXECUTE FUNCTION update_playlist_updated_at();

-- Comments for documentation
COMMENT ON TABLE playlists IS 'User-created music collections with privacy controls';
COMMENT ON COLUMN playlists.title IS 'Playlist name (1-200 characters)';
COMMENT ON COLUMN playlists.owner_user_id IS 'User who created the playlist (FK to users.id)';
COMMENT ON COLUMN playlists.is_public IS 'Privacy setting: TRUE=public, FALSE=private (default)';
COMMENT ON INDEX idx_playlists_public IS 'Partial index for efficient public playlist queries';
