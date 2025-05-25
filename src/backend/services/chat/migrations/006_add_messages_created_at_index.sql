-- Add created_at index for messages table
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at); 