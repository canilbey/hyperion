-- Add name index for roles table
CREATE INDEX IF NOT EXISTS idx_roles_name ON roles(name); 