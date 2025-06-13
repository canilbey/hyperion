-- Create files table for file metadata
CREATE TABLE IF NOT EXISTS files (
    file_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_filename VARCHAR(255) NOT NULL,
    content_type VARCHAR(100) NOT NULL,
    original_size BIGINT NOT NULL,
    num_chunks INTEGER NOT NULL,
    chunked_total_size BIGINT NOT NULL,
    upload_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    user_id UUID,
    -- İleride user entegrasyonu için foreign key eklenebilir
    CONSTRAINT fk_user FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_files_upload_time ON files(upload_time); 