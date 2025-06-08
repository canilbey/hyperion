-- Add context_window column to chat_contexts table (idempotent)
ALTER TABLE chat_contexts
ADD COLUMN IF NOT EXISTS context_window JSONB DEFAULT '[]'::jsonb; 