-- Create models table
CREATE TABLE IF NOT EXISTS models (
    model_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider VARCHAR(50) NOT NULL,
    model_name VARCHAR(100) UNIQUE NOT NULL,
    model VARCHAR(100) NOT NULL,
    system_prompt TEXT,
    api_key TEXT,
    knowledge_table_name VARCHAR(100),
    knowledge_table_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
); 