-- Chat service: Create context management tables
-- Migration: Create tables for chat context management

-- Enable UUID extension if not enabled
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create chat contexts table
CREATE TABLE IF NOT EXISTS chat_contexts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID REFERENCES chats(chat_id) ON DELETE CASCADE,
    token_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create chat context messages table
CREATE TABLE IF NOT EXISTS chat_context_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    context_id UUID REFERENCES chat_contexts(id) ON DELETE CASCADE,
    message_id BIGINT REFERENCES messages(message_id) ON DELETE CASCADE,
    token_count INTEGER DEFAULT 0,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_chat_contexts_chat_id ON chat_contexts(chat_id);
CREATE INDEX IF NOT EXISTS idx_chat_context_messages_context_id ON chat_context_messages(context_id);
CREATE INDEX IF NOT EXISTS idx_chat_context_messages_message_id ON chat_context_messages(message_id);

-- Add column comments (all in English)
COMMENT ON TABLE chat_contexts IS 'Stores chat context metadata';
COMMENT ON TABLE chat_context_messages IS 'Stores messages within chat contexts';
COMMENT ON COLUMN chat_contexts.token_count IS 'Total token count in context window';
COMMENT ON COLUMN chat_contexts.metadata IS 'Additional context metadata (model info, settings, etc.)';
COMMENT ON COLUMN chat_context_messages.token_count IS 'Token count for this message';
COMMENT ON COLUMN chat_context_messages.role IS 'Message role (system, user, assistant)';
COMMENT ON COLUMN chat_context_messages.content IS 'Message content'; 