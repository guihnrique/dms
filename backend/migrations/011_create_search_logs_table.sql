-- Migration 011: Create search_logs table
-- Task 1.1
-- Requirements: 12

CREATE TABLE IF NOT EXISTS search_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    query_text VARCHAR(500) NOT NULL,
    result_count INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    -- Foreign key with SET NULL on user deletion (support guest searches)
    CONSTRAINT fk_search_logs_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE SET NULL
);

-- Index for temporal queries
CREATE INDEX idx_search_logs_created_at ON search_logs(created_at);

-- Index for trend analysis
CREATE INDEX idx_search_logs_query_text ON search_logs(query_text);

-- Comments
COMMENT ON TABLE search_logs IS 'Search query logging for analytics (Task 1.1, Requirement 12)';
COMMENT ON COLUMN search_logs.user_id IS 'Nullable to support guest (unauthenticated) searches';
COMMENT ON COLUMN search_logs.query_text IS 'Search query text (max 500 chars)';
COMMENT ON COLUMN search_logs.result_count IS 'Total number of results returned';
