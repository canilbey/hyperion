-- Add label index for chats table
CREATE INDEX IF NOT EXISTS idx_chats_label ON chats(label); 