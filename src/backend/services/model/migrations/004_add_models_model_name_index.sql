-- Add model_name index for models table
CREATE INDEX IF NOT EXISTS idx_models_model_name ON models(model_name); 