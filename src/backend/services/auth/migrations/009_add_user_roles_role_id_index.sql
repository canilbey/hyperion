-- Add role_id index for user_roles table
CREATE INDEX IF NOT EXISTS idx_user_roles_role_id ON user_roles(role_id); 