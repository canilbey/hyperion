-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    message_id BIGSERIAL PRIMARY KEY,
    chat_id UUID REFERENCES chats(chat_id) ON DELETE CASCADE,
    role VARCHAR(10) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    usage JSONB,
    chat_name VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
); 