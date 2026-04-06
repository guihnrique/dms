-- Migration: Create review_votes table
-- Task 1.2: Review votes table with unique constraint
-- Requirements: 7 (Helpfulness Voting)

CREATE TABLE review_votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    review_id UUID NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
    vote_type VARCHAR(20) NOT NULL CHECK (vote_type IN ('helpful', 'not_helpful')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- One vote per user per review
    CONSTRAINT unique_user_review_vote UNIQUE (user_id, review_id)
);

-- Index for vote count queries
CREATE INDEX idx_review_votes_review_id ON review_votes(review_id);
CREATE INDEX idx_review_votes_user_id ON review_votes(user_id);

-- Trigger for automatic updated_at
CREATE OR REPLACE FUNCTION update_review_votes_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_review_votes_updated_at
    BEFORE UPDATE ON review_votes
    FOR EACH ROW
    EXECUTE FUNCTION update_review_votes_updated_at();

-- Comments
COMMENT ON TABLE review_votes IS 'User votes on review helpfulness';
COMMENT ON COLUMN review_votes.vote_type IS 'helpful or not_helpful';
COMMENT ON CONSTRAINT unique_user_review_vote ON review_votes IS 'Prevent duplicate votes per user per review';
