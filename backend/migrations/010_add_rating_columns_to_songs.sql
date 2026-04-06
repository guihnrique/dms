-- Migration: Add average rating columns to songs table
-- Task 1.3: Denormalized rating data for performance
-- Requirements: 6 (Average Rating Calculation), 12 (Display Reviews with Songs)

ALTER TABLE songs
    ADD COLUMN average_rating DECIMAL(2,1) CHECK (average_rating >= 1.0 AND average_rating <= 5.0),
    ADD COLUMN review_count INTEGER NOT NULL DEFAULT 0;

-- Index for sorting songs by rating
CREATE INDEX idx_songs_average_rating ON songs(average_rating DESC NULLS LAST);

-- Initialize existing songs
UPDATE songs SET review_count = 0 WHERE review_count IS NULL;

-- Comments
COMMENT ON COLUMN songs.average_rating IS 'Average rating from all non-flagged reviews (1.0-5.0, NULL if no reviews)';
COMMENT ON COLUMN songs.review_count IS 'Total count of non-flagged reviews';
