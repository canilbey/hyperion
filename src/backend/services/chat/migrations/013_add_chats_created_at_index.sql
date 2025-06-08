-- Add created_at index for chats table
CREATE INDEX IF NOT EXISTS idx_chats_created_at ON chats(created_at); 