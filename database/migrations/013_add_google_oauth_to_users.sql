-- Migration 013: Add Google OAuth support to users table
--
-- Makes password_hash and salt nullable (OAuth users have no password)
-- Adds google_id column for linking Google accounts
-- Adds auth_provider column to track how the user signed up

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS google_id TEXT UNIQUE,
    ADD COLUMN IF NOT EXISTS auth_provider TEXT NOT NULL DEFAULT 'email',
    ALTER COLUMN password_hash DROP NOT NULL,
    ALTER COLUMN salt DROP NOT NULL;

-- Index for fast Google ID lookups during OAuth callback
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);
