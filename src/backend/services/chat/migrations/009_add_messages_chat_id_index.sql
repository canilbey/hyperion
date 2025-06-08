-- Add chat_id index for messages table
CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id); 