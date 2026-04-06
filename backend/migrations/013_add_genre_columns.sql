-- Migration 013: Add genre columns to songs and albums
-- Task 1.3
-- Requirements: 3

-- Add genre to songs table if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'songs'
        AND column_name = 'genre'
    ) THEN
        ALTER TABLE songs ADD COLUMN genre VARCHAR(100);
    END IF;
END $$;

-- Add genre to albums table if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'albums'
        AND column_name = 'genre'
    ) THEN
        ALTER TABLE albums ADD COLUMN genre VARCHAR(100);
    END IF;
END $$;

-- Add indexes for filtering queries
CREATE INDEX IF NOT EXISTS idx_songs_genre ON songs(genre);
CREATE INDEX IF NOT EXISTS idx_albums_genre ON albums(genre);

-- Comments
COMMENT ON COLUMN songs.genre IS 'Music genre for filtering (Task 1.3, Requirement 3)';
COMMENT ON COLUMN albums.genre IS 'Music genre for filtering (Task 1.3, Requirement 3)';
