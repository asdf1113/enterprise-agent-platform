from transformers import AutoTokenizer

from rag.chunking import chunk_documents
from rag.embedding import BgeM3Embedder
from rag.parser import load_documents
from settings import get_settings
from storage.database import Database
from storage.vectorstore import KnowledgeVectorStore


def main() -> None:
    settings = get_settings()

    print(
        f"Loading documents from knowledge corpus..."
    )

    documents = load_documents()

    print(
        f"documents: {len(documents)}"
    )

    print(
        f"Loading tokenizer: "
        f"{settings.embedding_model}"
    )

    tokenizer = AutoTokenizer.from_pretrained(
        settings.embedding_model,
        use_fast=True,
    )

    chunks = chunk_documents(
        documents,
        tokenizer,
        max_tokens=settings.embedding_max_tokens,
        overlap_tokens=(
            settings.embedding_overlap_tokens
        ),
    )

    print(
        f"chunks: {len(chunks)}"
    )

    print(
        f"Loading embedding model: "
        f"{settings.embedding_model}"
    )

    embedder = BgeM3Embedder(
        settings.embedding_model,
        max_sequence_length=(
            settings.embedding_max_sequence_length
        ),
    )

    embeddings = embedder.encode(
        [
            chunk.content
            for chunk in chunks
        ],
        batch_size=settings.embedding_batch_size,
    )

    print(
        f"embedding dimension: "
        f"{len(embeddings[0])}"
    )

    database = Database(settings)

    vectorstore = KnowledgeVectorStore(
        database
    )

    vectorstore.replace_chunks(
        chunks,
        embeddings,
        embedding_model=settings.embedding_model,
    )

    print(
        f"Ingested {len(chunks)} chunks "
        f"from {len(documents)} documents."
    )


if __name__ == "__main__":
    main()
