-- Migration 015: Add photo_url to artists table
-- Add artist photo URL field

ALTER TABLE artists
ADD COLUMN photo_url TEXT;

-- Add comment
COMMENT ON COLUMN artists.photo_url IS 'URL for artist profile photo';
