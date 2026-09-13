from functools import lru_cache

from models.gateway import ModelGateway
from settings import get_settings
from storage.database import Database

from rag.embedding import BgeM3Embedder
from rag.reranker import BgeReranker
from rag.retriever import (
    DenseKnowledgeRetriever,
    KnowledgeRetriever,
)


@lru_cache
def get_model_gateway() -> ModelGateway:
    return ModelGateway(get_settings())


@lru_cache
def get_database() -> Database:
    return Database(get_settings())

@lru_cache
def get_knowledge_retriever() -> KnowledgeRetriever:
    settings = get_settings()

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

    return KnowledgeRetriever(
        embedder=embedder,
        vectorstore=DenseKnowledgeRetriever(
            get_database()
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