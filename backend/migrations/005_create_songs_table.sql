-- Migration 005: Create songs table with album relationship and soft delete
-- Task 1.3 - Requirements: 8.1, 8.2, 8.3, 8.4, 11.1, 11.2, 12.1, 12.4, 12.6, 13.4

-- Create songs table
CREATE TABLE IF NOT EXISTS songs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    album_id INTEGER NOT NULL REFERENCES albums(id) ON DELETE CASCADE,
    duration_seconds INTEGER NOT NULL CHECK (duration_seconds BETWEEN 1 AND 7200),
    genre VARCHAR(50),
    year INTEGER,
    external_links JSONB,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Create index on album_id for FK lookup performance
-- Requirement 13.4: Implement indexes for performance
CREATE INDEX IF NOT EXISTS idx_songs_album_id ON songs(album_id);

-- Create index on deleted_at for soft delete filtering
-- Requirement 11.3: Exclude deleted songs from queries
CREATE INDEX IF NOT EXISTS idx_songs_deleted_at ON songs(deleted_at);

-- Create partial index on id WHERE deleted_at IS NULL for active songs
-- Requirement 13.4: Optimize performance for active songs
CREATE INDEX IF NOT EXISTS idx_songs_active ON songs(id) WHERE deleted_at IS NULL;

-- Create trigram GIN index on title for search
-- Requirement 13.4: Search performance
CREATE INDEX IF NOT EXISTS idx_songs_title_trgm ON songs USING GIN (title gin_trgm_ops);

-- Create index on genre for filtering
-- Requirement 13.4: Genre filtering performance
CREATE INDEX IF NOT EXISTS idx_songs_genre ON songs(genre);

-- Create trigger for automatic updated_at timestamp
CREATE TRIGGER update_songs_updated_at
BEFORE UPDATE ON songs
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE songs IS 'Music catalog songs with soft delete - Requirement 8.1-8.9, 11.1-11.7';
COMMENT ON COLUMN songs.title IS 'Song title (1-200 characters) - Requirement 8.2';
COMMENT ON COLUMN songs.album_id IS 'Foreign key to albums table - Requirement 8.3';
COMMENT ON COLUMN songs.duration_seconds IS 'Song duration in seconds (1-7200) - Requirement 8.4';
COMMENT ON COLUMN songs.deleted_at IS 'Soft delete timestamp - Requirement 11.1, 11.2';
COMMENT ON CONSTRAINT songs_album_id_fkey ON songs IS 'ON DELETE CASCADE - Requirement 12.1';
COMMENT ON CONSTRAINT songs_duration_seconds_check ON songs IS 'Duration must be between 1 and 7200 seconds - Requirement 8.4';
