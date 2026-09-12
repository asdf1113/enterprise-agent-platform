ALTER TABLE knowledge_chunks
    ADD COLUMN IF NOT EXISTS document_group TEXT NOT NULL DEFAULT '';

ALTER TABLE knowledge_chunks
    ALTER COLUMN document_group DROP DEFAULT;

CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_document_group
    ON knowledge_chunks(document_group);
