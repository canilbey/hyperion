-- ParentChunk tablosu
CREATE TABLE IF NOT EXISTS parent_chunks (
    id SERIAL PRIMARY KEY,
    document_id UUID NOT NULL REFERENCES files(file_id) ON DELETE CASCADE,
    title VARCHAR(255),
    content TEXT NOT NULL,
    "order" INTEGER,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_parent_chunks_document_id ON parent_chunks(document_id);

-- ChildChunk tablosu
CREATE TABLE IF NOT EXISTS child_chunks (
    id SERIAL PRIMARY KEY,
    parent_id INTEGER NOT NULL REFERENCES parent_chunks(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    type VARCHAR(32),
    "order" INTEGER,
    embedding TEXT, -- Milvus ile uyumlu olacak şekilde, gerekirse TEXT olarak tutulabilir
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_child_chunks_parent_id ON child_chunks(parent_id); 