-- Add chat_name column to messages table
ALTER TABLE messages ADD COLUMN chat_name VARCHAR(255);

-- Create index for chat_name
CREATE INDEX IF NOT EXISTS idx_messages_chat_name ON messages(chat_name);

-- Update existing messages to set chat_name from chats table
UPDATE messages m
SET chat_name = c.label
FROM chats c
WHERE m.chat_id = c.chat_id;