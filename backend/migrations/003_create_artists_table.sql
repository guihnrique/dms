-- Migration 003: Create artists table with trigram GIN indexes
-- Task 1.1 - Requirements: 1.1, 1.2, 1.3, 1.4, 3.4, 13.4

-- Enable pg_trgm extension if not already enabled (for trigram search)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create artists table
CREATE TABLE IF NOT EXISTS artists (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    country CHAR(2) NOT NULL,  -- ISO 3166-1 alpha-2 country code
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Create trigram GIN index on name column for fast search
-- Requirement 3.4: Search performance (<200ms for 10k artists)
CREATE INDEX IF NOT EXISTS idx_artists_name_trgm ON artists USING GIN (name gin_trgm_ops);

-- Create standard B-tree index on country column for filtering
-- Requirement 13.4: Implement indexes for performance
CREATE INDEX IF NOT EXISTS idx_artists_country ON artists(country);

-- Create trigger function for automatic updated_at timestamp
-- Reuse function from previous migration if exists
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger on artists table
CREATE TRIGGER update_artists_updated_at
BEFORE UPDATE ON artists
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE artists IS 'Music catalog artists - Requirement 1.1-1.8';
COMMENT ON COLUMN artists.name IS 'Artist name (1-200 characters) - Requirement 1.2';
COMMENT ON COLUMN artists.country IS 'ISO 3166-1 alpha-2 country code - Requirement 1.3';
COMMENT ON INDEX idx_artists_name_trgm IS 'Trigram GIN index for fast artist search - Requirement 3.4';
