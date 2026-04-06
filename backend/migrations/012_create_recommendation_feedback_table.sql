-- Migration 012: Create recommendation_feedback table
-- Task 1.2
-- Requirements: 11

CREATE TABLE IF NOT EXISTS recommendation_feedback (
    user_id INTEGER NOT NULL,
    song_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    -- Composite primary key
    PRIMARY KEY (user_id, song_id),

    -- Foreign keys
    CONSTRAINT fk_recommendation_feedback_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_recommendation_feedback_song
        FOREIGN KEY (song_id)
        REFERENCES songs(id)
        ON DELETE CASCADE,

    -- Check constraint for action values
    CONSTRAINT chk_recommendation_feedback_action
        CHECK (action IN ('accepted', 'dismissed', 'clicked'))
);

-- Indexes for feedback queries
CREATE INDEX idx_recommendation_feedback_user_id ON recommendation_feedback(user_id);
CREATE INDEX idx_recommendation_feedback_song_id ON recommendation_feedback(song_id);

-- Comments
COMMENT ON TABLE recommendation_feedback IS 'User feedback on recommendations (Task 1.2, Requirement 11)';
COMMENT ON COLUMN recommendation_feedback.action IS 'User action: accepted (added to playlist), dismissed, or clicked';
COMMENT ON CONSTRAINT chk_recommendation_feedback_action ON recommendation_feedback IS 'Validates action is one of: accepted, dismissed, clicked';
