-- Add provider index for models table
CREATE INDEX IF NOT EXISTS idx_models_provider ON models(provider); 