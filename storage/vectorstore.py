import json

from sqlalchemy import text

from rag.chunking import KnowledgeChunk
from storage.database import Database


class KnowledgeVectorStore:
    def __init__(
        self,
        database: Database,
    ) -> None:
        self.engine = database.engine

    def replace_chunks(
        self,
        chunks: list[KnowledgeChunk],
        embeddings: list[list[float]],
        *,
        embedding_model: str,
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError(
                "Chunk and embedding counts differ"
            )

        document_ids = sorted(
            {
                chunk.document_id
                for chunk in chunks
            }
        )

        insert_statement = text(
            """
            INSERT INTO knowledge_chunks (
                chunk_id,
                document_id,
                document_name,
                document_type,
                department,
                version,
                effective_date,
                product,
                region,
                allowed_roles,
                source_path,
                section_title,
                chunk_index,
                token_count,
                content,
                embedding_model,
                embedding
            )
            VALUES (
                :chunk_id,
                :document_id,
                :document_name,
                :document_type,
                :department,
                :version,
                :effective_date,
                :product,
                :region,
                :allowed_roles,
                :source_path,
                :section_title,
                :chunk_index,
                :token_count,
                :content,
                :embedding_model,
                CAST(:embedding AS vector)
            )
            """
        )

        rows = []

        for chunk, embedding in zip(
            chunks,
            embeddings,
            strict=True,
        ):
            rows.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "document_id": chunk.document_id,
                    "document_name": (
                        chunk.document_name
                    ),
                    "document_type": (
                        chunk.document_type
                    ),
                    "department": chunk.department,
                    "version": chunk.version,
                    "effective_date": (
                        chunk.effective_date
                    ),
                    "product": chunk.product,
                    "region": chunk.region,
                    "allowed_roles": list(
                        chunk.allowed_roles
                    ),
                    "source_path": chunk.source_path,
                    "section_title": (
                        chunk.section_title
                    ),
                    "chunk_index": chunk.chunk_index,
                    "token_count": chunk.token_count,
                    "content": chunk.content,
                    "embedding_model": embedding_model,
                    "embedding": json.dumps(
                        embedding,
                        separators=(",", ":"),
                    ),
                }
            )

        with self.engine.begin() as connection:
            for document_id in document_ids:
                connection.execute(
                    text(
                        """
                        DELETE FROM knowledge_chunks
                        WHERE document_id = :document_id
                        """
                    ),
                    {
                        "document_id": document_id,
                    },
                )

            if rows:
                connection.execute(
                    insert_statement,
                    rows,
                )
