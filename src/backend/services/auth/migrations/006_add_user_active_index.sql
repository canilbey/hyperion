-- Add is_active index for users table
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active); 