-- Add created_at index for models table
CREATE INDEX IF NOT EXISTS idx_models_created_at ON models(created_at); 