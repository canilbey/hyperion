-- Migration: Insert default role "user"
INSERT INTO roles (name, description) VALUES ('user', 'Regular user with basic access') ON CONFLICT (name) DO NOTHING; 