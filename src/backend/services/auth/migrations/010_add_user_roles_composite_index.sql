-- Add composite index for faster role lookups
CREATE INDEX IF NOT EXISTS idx_user_roles_user_role ON user_roles(user_id, role_id); 