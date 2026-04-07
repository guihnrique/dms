-- Migration 014: Create favorites table
-- Add user favorites for songs and albums

CREATE TABLE IF NOT EXISTS favorites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    song_id INTEGER REFERENCES songs(id) ON DELETE CASCADE,
    album_id INTEGER REFERENCES albums(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,

    -- Constraint: Either song_id or album_id must be set, but not both
    CONSTRAINT favorite_type_check CHECK (
        (song_id IS NOT NULL AND album_id IS NULL) OR
        (song_id IS NULL AND album_id IS NOT NULL)
    )
);

-- Create unique indexes to prevent duplicate favorites
CREATE UNIQUE INDEX IF NOT EXISTS idx_favorites_user_song ON favorites(user_id, song_id) WHERE song_id IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_favorites_user_album ON favorites(user_id, album_id) WHERE album_id IS NOT NULL;

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_favorites_user_id ON favorites(user_id);
