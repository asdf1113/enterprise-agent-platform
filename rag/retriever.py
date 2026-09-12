import json
from dataclasses import dataclass, replace
from datetime import date

from sqlalchemy import text

from storage.database import Database


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str

    document_id: str
    document_group: str
    document_name: str
    document_type: str

    version: str
    effective_date: date

    product: str
    region: str

    source_path: str
    section_title: str
    content: str

    dense_score: float
    rerank_score: float | None = None

    @property
    def citation(self) -> str:
        return (
            f"{self.document_name}"
            f" / {self.section_title}"
            f" ({self.version})"
        )


class DenseKnowledgeRetriever:
    def __init__(
        self,
        database: Database,
    ) -> None:
        self.engine = database.engine

    def search(
        self,
        query_embedding: list[float],
        *,
        role: str,
        as_of_date: date,
        limit: int,
        product: str | None = None,
        region: str | None = None,
    ) -> list[RetrievedChunk]:
        conditions = [
            "effective_date <= :as_of_date",
        ]

        params = {
            "query_embedding": json.dumps(
                query_embedding,
                separators=(",", ":"),
            ),
            "role": role,
            "as_of_date": as_of_date,
            "limit": limit,
        }

        if product is not None:
            conditions.append(
                "(product = 'all' OR lower(product) = lower(:product))"
            )
            params["product"] = product

        if region is not None:
            conditions.append(
                "(region = 'all' OR lower(region) = lower(:region))"
            )
            params["region"] = region

        where_clause = "\nAND ".join(conditions)

        statement = text(
            f"""
            WITH versioned AS (
                SELECT
                    *,
                    MAX(effective_date) OVER (
                        PARTITION BY document_group
                    ) AS latest_effective_date
                FROM knowledge_chunks
                WHERE {where_clause}
            ),
            eligible AS (
                SELECT *
                FROM versioned
                WHERE
                    effective_date = latest_effective_date
                    AND :role = ANY(allowed_roles)
            )
            SELECT
                chunk_id,
                document_id,
                document_group,
                document_name,
                document_type,
                version,
                effective_date,
                product,
                region,
                source_path,
                section_title,
                content,
                1 - (
                    embedding
                    <=>
                    CAST(:query_embedding AS vector)
                ) AS dense_score
            FROM eligible
            ORDER BY
                embedding
                <=>
                CAST(:query_embedding AS vector)
            LIMIT :limit
            """
        )

        with self.engine.connect() as connection:
            rows = (
                connection.execute(
                    statement,
                    params,
                )
                .mappings()
                .all()
            )

        return [
            RetrievedChunk(
                chunk_id=row["chunk_id"],
                document_id=row["document_id"],
                document_group=row["document_group"],
                document_name=row["document_name"],
                document_type=row["document_type"],
                version=row["version"],
                effective_date=row["effective_date"],
                product=row["product"],
                region=row["region"],
                source_path=row["source_path"],
                section_title=row["section_title"],
                content=row["content"],
                dense_score=float(row["dense_score"]),
            )
            for row in rows
        ]

class KnowledgeRetriever:
    def __init__(
        self,
        *,
        embedder,
        vectorstore: DenseKnowledgeRetriever,
        reranker,
        candidate_k: int,
        top_k: int,
        embedding_batch_size: int,
        reranker_batch_size: int,
    ) -> None:
        self.embedder = embedder
        self.vectorstore = vectorstore
        self.reranker = reranker

        self.candidate_k = candidate_k
        self.top_k = top_k

        self.embedding_batch_size = (
            embedding_batch_size
        )
        self.reranker_batch_size = (
            reranker_batch_size
        )

    def search(
        self,
        query: str,
        *,
        role: str,
        as_of_date: date,
        product: str | None = None,
        region: str | None = None,
    ) -> list[RetrievedChunk]:
        query_embedding = self.embedder.encode(
            [query],
            batch_size=self.embedding_batch_size,
        )[0]

        candidates = self.vectorstore.search(
            query_embedding,
            role=role,
            as_of_date=as_of_date,
            product=product,
            region=region,
            limit=self.candidate_k,
        )

        return self.reranker.rerank(
            query,
            candidates,
            batch_size=self.reranker_batch_size,
            top_k=self.top_k,
        )