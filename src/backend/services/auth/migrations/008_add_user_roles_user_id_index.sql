-- Add user_id index for user_roles table
CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id); 