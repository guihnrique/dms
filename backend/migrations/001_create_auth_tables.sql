-- Migration 001: Create authentication tables
-- Task 1.1: Database schema and models setup
-- Requirements: 1.1, 1.2, 1.3, 2.1, 12.1, 12.2, 12.3, 13.1

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    failed_login_attempts INTEGER DEFAULT 0,
    account_locked_until TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create unique index on email (enforces uniqueness at database level)
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Create partial index on account_locked_until for lockout queries
-- Only indexes rows where account is actually locked (performance optimization)
CREATE INDEX IF NOT EXISTS idx_users_locked
ON users(account_locked_until)
WHERE account_locked_until IS NOT NULL;

-- Create function for automatic updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at on row updates
CREATE TRIGGER update_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Create auth_audit_log table for authentication event tracking
CREATE TABLE IF NOT EXISTS auth_audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    email VARCHAR(255) NOT NULL,
    event_type VARCHAR(50) NOT NULL,  -- 'login_success', 'login_failure', 'logout', 'register'
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes on auth_audit_log for efficient queries
CREATE INDEX IF NOT EXISTS idx_auth_audit_user_time
ON auth_audit_log(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_auth_audit_email_time
ON auth_audit_log(email, created_at DESC);

-- Add comments for documentation
COMMENT ON TABLE users IS 'User accounts with authentication credentials and security tracking';
COMMENT ON COLUMN users.password_hash IS 'Bcrypt hashed password (never store plain text)';
COMMENT ON COLUMN users.failed_login_attempts IS 'Counter for brute force protection';
COMMENT ON COLUMN users.account_locked_until IS 'Timestamp when account lockout expires (NULL = not locked)';

COMMENT ON TABLE auth_audit_log IS 'Authentication event audit trail for security monitoring';
COMMENT ON COLUMN auth_audit_log.event_type IS 'Type of authentication event (login_success, login_failure, logout, register)';
