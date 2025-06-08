-- NOTE: Token limits should be externalized to a configuration file for maintainability.
-- See src/backend/config/models.py for the canonical source.
--
-- Model service: Add token limit and related columns (PostgreSQL 9.6+ gerektirir)
-- Migration: Add token limit, max tokens, temperature and active status columns
-- This migration is idempotent and compatible with asyncpg.

-- Add new columns
ALTER TABLE models
ADD COLUMN IF NOT EXISTS token_limit INTEGER,
ADD COLUMN IF NOT EXISTS max_tokens INTEGER,
ADD COLUMN IF NOT EXISTS temperature FLOAT DEFAULT 0.7,
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

-- Update existing models with official max_tokens values (2024 specs)
UPDATE models
SET max_tokens = CASE
    WHEN model LIKE 'gpt-4%' THEN 8192
    WHEN model LIKE 'gpt-3.5%' THEN 16384
    WHEN model LIKE 'claude-3%' THEN 200000
    WHEN model LIKE 'deepseek%' THEN 128000
    WHEN model LIKE 'mistral large 2%' THEN 128000
    WHEN model LIKE 'mistral nemo%' THEN 128000
    WHEN model LIKE 'mistral large%' THEN 32768
    WHEN model LIKE 'mistral%' THEN 32768
    ELSE 4000
END
WHERE max_tokens IS NULL;

-- Add column comments
COMMENT ON COLUMN models.token_limit IS 'User-defined token limit for context window (optional)';
COMMENT ON COLUMN models.max_tokens IS 'Model''s maximum token capacity';
COMMENT ON COLUMN models.temperature IS 'Model temperature parameter (0.0 to 2.0)';
COMMENT ON COLUMN models.is_active IS 'Whether the model is active and available for use';

-- Add index for active models
CREATE INDEX IF NOT EXISTS idx_models_is_active ON models(is_active);

-- Add index for token limit queries
CREATE INDEX IF NOT EXISTS idx_models_token_limit ON models(token_limit) WHERE token_limit IS NOT NULL; 