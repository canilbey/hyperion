-- Minimal initial migration for chat tables

-- Chat containers
CREATE TABLE IF NOT EXISTS chats (
    chat_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    label VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Message storage
CREATE TABLE IF NOT EXISTS messages (
    message_id BIGSERIAL PRIMARY KEY,
    chat_id UUID REFERENCES chats(chat_id) ON DELETE CASCADE,
    role VARCHAR(10) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    usage JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id);