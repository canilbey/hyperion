-- Add email index for users table
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email); 