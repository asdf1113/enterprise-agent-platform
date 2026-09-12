CREATE TABLE IF NOT EXISTS knowledge_chunks (
    chunk_id TEXT PRIMARY KEY,

    document_id TEXT NOT NULL,
    document_name TEXT NOT NULL,
    document_type TEXT NOT NULL,
    department TEXT NOT NULL,

    version TEXT NOT NULL,
    effective_date DATE NOT NULL,

    product TEXT NOT NULL,
    region TEXT NOT NULL,
    allowed_roles TEXT[] NOT NULL,

    source_path TEXT NOT NULL,
    section_title TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    token_count INTEGER NOT NULL,

    content TEXT NOT NULL,

    embedding_model TEXT NOT NULL,
    embedding VECTOR(1024) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_document_id
    ON knowledge_chunks(document_id);

CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_document_type
    ON knowledge_chunks(document_type);

CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_product
    ON knowledge_chunks(product);

CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_region
    ON knowledge_chunks(region);

CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_effective_date
    ON knowledge_chunks(effective_date);
