from dataclasses import dataclass
from typing import Any

from rag.parser import ParsedDocument


@dataclass(frozen=True)
class KnowledgeChunk:
    chunk_id: str

    document_id: str
    document_name: str
    document_type: str
    department: str

    version: str
    effective_date: object

    product: str
    region: str
    allowed_roles: tuple[str, ...]

    source_path: str
    section_title: str
    chunk_index: int
    token_count: int

    content: str


def chunk_document(
    document: ParsedDocument,
    tokenizer: Any,
    *,
    max_tokens: int,
    overlap_tokens: int,
) -> list[KnowledgeChunk]:
    if max_tokens <= 0:
        raise ValueError("max_tokens must be positive")

    if overlap_tokens < 0:
        raise ValueError(
            "overlap_tokens must not be negative"
        )

    chunks: list[KnowledgeChunk] = []
    chunk_index = 0

    for section in document.sections:
        prefix = (
            f"{document.metadata.document_name}\n"
            f"{section.title}\n"
        )

        prefix_tokens = tokenizer.encode(
            prefix,
            add_special_tokens=False,
        )

        body_tokens = tokenizer.encode(
            section.content,
            add_special_tokens=False,
        )

        body_budget = max_tokens - len(prefix_tokens)

        if body_budget <= overlap_tokens:
            raise ValueError(
                "max_tokens is too small for "
                "document/section prefix"
            )

        step = body_budget - overlap_tokens
        start = 0

        while start < len(body_tokens):
            end = min(
                start + body_budget,
                len(body_tokens),
            )

            body_text = tokenizer.decode(
                body_tokens[start:end],
                skip_special_tokens=True,
            ).strip()

            content = (
                f"{prefix}{body_text}"
            ).strip()

            token_count = len(
                tokenizer.encode(
                    content,
                    add_special_tokens=False,
                )
            )

            chunks.append(
                KnowledgeChunk(
                    chunk_id=(
                        f"{document.metadata.document_id}:"
                        f"{chunk_index:04d}"
                    ),
                    document_id=(
                        document.metadata.document_id
                    ),
                    document_name=(
                        document.metadata.document_name
                    ),
                    document_type=(
                        document.metadata.document_type
                    ),
                    department=(
                        document.metadata.department
                    ),
                    version=document.metadata.version,
                    effective_date=(
                        document.metadata.effective_date
                    ),
                    product=document.metadata.product,
                    region=document.metadata.region,
                    allowed_roles=(
                        document.metadata.allowed_roles
                    ),
                    source_path=(
                        document.metadata.source_path
                    ),
                    section_title=section.title,
                    chunk_index=chunk_index,
                    token_count=token_count,
                    content=content,
                )
            )

            chunk_index += 1

            if end == len(body_tokens):
                break

            start += step

    return chunks


def chunk_documents(
    documents: list[ParsedDocument],
    tokenizer: Any,
    *,
    max_tokens: int,
    overlap_tokens: int,
) -> list[KnowledgeChunk]:
    chunks: list[KnowledgeChunk] = []

    for document in documents:
        chunks.extend(
            chunk_document(
                document,
                tokenizer,
                max_tokens=max_tokens,
                overlap_tokens=overlap_tokens,
            )
        )

    return chunks
