from datetime import date

from rag.embedding import BgeM3Embedder
from rag.reranker import BgeReranker
from rag.retriever import (
    DenseKnowledgeRetriever,
    KnowledgeRetriever,
)
from settings import get_settings
from storage.database import Database


def run_query(
    retriever: KnowledgeRetriever,
    query: str,
    *,
    role: str,
    as_of_date: date,
    product: str | None = None,
    region: str | None = None,
) -> None:
    print("\n" + "=" * 80)
    print("query:", query)
    print("role:", role)
    print("as_of_date:", as_of_date)

    results = retriever.search(
        query,
        role=role,
        as_of_date=as_of_date,
        product=product,
        region=region,
    )

    for index, result in enumerate(
        results,
        start=1,
    ):
        print(
            f"\n[{index}] "
            f"dense={result.dense_score:.4f} "
            f"rerank={result.rerank_score:.4f}"
        )
        print("citation:", result.citation)
        print("source:", result.source_path)
        print(result.content)


def main() -> None:
    settings = get_settings()

    database = Database(settings)

    embedder = BgeM3Embedder(
        settings.embedding_model,
        max_sequence_length=(
            settings.embedding_max_sequence_length
        ),
    )

    reranker = BgeReranker(
        settings.reranker_model,
        max_length=settings.reranker_max_length,
    )

    retriever = KnowledgeRetriever(
        embedder=embedder,
        vectorstore=DenseKnowledgeRetriever(
            database
        ),
        reranker=reranker,
        candidate_k=settings.retrieval_candidate_k,
        top_k=settings.retrieval_top_k,
        embedding_batch_size=(
            settings.embedding_batch_size
        ),
        reranker_batch_size=(
            settings.reranker_batch_size
        ),
    )

    run_query(
        retriever,
        "X200 的标准保修期多久？",
        role="support",
        as_of_date=date(2026, 9, 12),
        product="X200",
    )

    run_query(
        retriever,
        "华南地区2026年第二季度X200的销售激励是多少？",
        role="sales",
        as_of_date=date(2026, 6, 30),
        product="X200",
        region="south_china",
    )

    run_query(
        retriever,
        "创建返修工单前需要准备哪些信息？",
        role="support",
        as_of_date=date(2026, 9, 12),
    )


if __name__ == "__main__":
    main()
