-- Migration 004: Create albums table with artist relationship
-- Task 1.2 - Requirements: 5.1, 5.2, 5.3, 6.2, 12.2, 12.6, 13.4

-- Create albums table
CREATE TABLE IF NOT EXISTS albums (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    artist_id INTEGER NOT NULL REFERENCES artists(id) ON DELETE RESTRICT,
    release_year INTEGER NOT NULL,
    album_cover_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Create index on artist_id for FK lookup performance
-- Requirement 13.4: Implement indexes for performance
CREATE INDEX IF NOT EXISTS idx_albums_artist_id ON albums(artist_id);

-- Create index on release_year DESC for sorting
-- Requirement 6.2: Order by release_year DESC, title ASC
CREATE INDEX IF NOT EXISTS idx_albums_release_year ON albums(release_year DESC);

-- Create trigram GIN index on title for search
-- Requirement 13.4: Search performance
CREATE INDEX IF NOT EXISTS idx_albums_title_trgm ON albums USING GIN (title gin_trgm_ops);

-- Create trigger for automatic updated_at timestamp
CREATE TRIGGER update_albums_updated_at
BEFORE UPDATE ON albums
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE albums IS 'Music catalog albums - Requirement 5.1-5.9';
COMMENT ON COLUMN albums.title IS 'Album title (1-200 characters) - Requirement 5.2';
COMMENT ON COLUMN albums.artist_id IS 'Foreign key to artists table - Requirement 5.3';
COMMENT ON COLUMN albums.release_year IS 'Album release year (1900 to current_year + 1) - Requirement 5.4';
COMMENT ON CONSTRAINT albums_artist_id_fkey ON albums IS 'ON DELETE RESTRICT - Requirement 12.2';
