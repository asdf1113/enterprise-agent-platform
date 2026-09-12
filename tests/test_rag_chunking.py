from datetime import date

from rag.chunking import chunk_document
from rag.parser import (
    DocumentMetadata,
    DocumentSection,
    ParsedDocument,
)


class CharacterTokenizer:
    def encode(
        self,
        text: str,
        add_special_tokens: bool = False,
    ) -> list[int]:
        return [
            ord(character)
            for character in text
        ]

    def decode(
        self,
        tokens: list[int],
        skip_special_tokens: bool = True,
    ) -> str:
        return "".join(
            chr(token)
            for token in tokens
        )


def test_chunking_respects_section_boundaries() -> None:
    document = ParsedDocument(
        metadata=DocumentMetadata(
            document_id="doc-1",
            document_name="测试文档",
            document_type="test",
            department="test",
            version="1",
            effective_date=date(2026, 1, 1),
            product="X200",
            region="all",
            allowed_roles=("support",),
            source_path="test.md",
        ),
        sections=(
            DocumentSection(
                title="章节A",
                content="A" * 60,
            ),
            DocumentSection(
                title="章节B",
                content="B" * 20,
            ),
        ),
    )

    chunks = chunk_document(
        document,
        CharacterTokenizer(),
        max_tokens=30,
        overlap_tokens=5,
    )

    assert len(chunks) > 2

    assert all(
        chunk.token_count <= 30
        for chunk in chunks
    )

    assert any(
        chunk.section_title == "章节A"
        for chunk in chunks
    )

    assert any(
        chunk.section_title == "章节B"
        for chunk in chunks
    )

    assert len(
        {
            chunk.chunk_id
            for chunk in chunks
        }
    ) == len(chunks)
