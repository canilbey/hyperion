-- Insert default roles
INSERT INTO roles (name, description) VALUES
    ('admin', 'System administrator with full access'),
    ('user', 'Regular user with standard access')
ON CONFLICT (name) DO NOTHING; 