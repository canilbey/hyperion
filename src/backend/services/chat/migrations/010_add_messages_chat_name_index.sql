-- Add chat_name index for messages table
CREATE INDEX IF NOT EXISTS idx_messages_chat_name ON messages(chat_name); 