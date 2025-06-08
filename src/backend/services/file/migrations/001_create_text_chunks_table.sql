CREATE TABLE IF NOT EXISTS text_chunks (
    id SERIAL PRIMARY KEY,
    file_id VARCHAR(64) NOT NULL,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_text_chunks_file_id ON text_chunks(file_id); 