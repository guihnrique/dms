-- Migration: Create reviews table
-- Task 1.1: Reviews table with rating constraints and unique constraint
-- Requirements: 1 (Submit Review), 10 (One Review Per User Per Song)

CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    song_id INTEGER NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    body TEXT CHECK (LENGTH(body) <= 2000),
    is_flagged BOOLEAN NOT NULL DEFAULT FALSE,
    helpful_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- One review per user per song
    CONSTRAINT unique_user_song_review UNIQUE (user_id, song_id)
);

-- Indexes for query performance
CREATE INDEX idx_reviews_song_id ON reviews(song_id);
CREATE INDEX idx_reviews_user_id ON reviews(user_id);
CREATE INDEX idx_reviews_created_at ON reviews(created_at DESC);
CREATE INDEX idx_reviews_flagged ON reviews(is_flagged) WHERE is_flagged = TRUE;

-- Trigger for automatic updated_at
CREATE OR REPLACE FUNCTION update_reviews_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_reviews_updated_at
    BEFORE UPDATE ON reviews
    FOR EACH ROW
    EXECUTE FUNCTION update_reviews_updated_at();

-- Comments
COMMENT ON TABLE reviews IS 'User reviews for songs with ratings (1-5)';
COMMENT ON COLUMN reviews.rating IS 'Rating value between 1 and 5';
COMMENT ON COLUMN reviews.body IS 'Optional review text (max 2000 chars)';
COMMENT ON COLUMN reviews.is_flagged IS 'True if review contains inappropriate content';
COMMENT ON COLUMN reviews.helpful_count IS 'Number of users who found this review helpful';
COMMENT ON CONSTRAINT unique_user_song_review ON reviews IS 'Enforce one review per user per song';
