-- Migration: Insert default role "admin"
INSERT INTO roles (name, description) VALUES ('admin', 'Administrator with full access') ON CONFLICT (name) DO NOTHING; 