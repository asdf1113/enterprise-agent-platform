from rag.parser import load_documents


def test_parser_preserves_document_sections() -> None:
    documents = load_documents()

    assert len(documents) == 7

    warranty = next(
        document
        for document in documents
        if document.metadata.document_id
        == "warranty-policy-2026"
    )

    titles = {
        section.title
        for section in warranty.sections
    }

    assert "标准保修期限" in titles
    assert "服务范围" in titles
    assert "返修流程" in titles
    assert "版本说明" in titles

    standard_warranty = next(
        section
        for section in warranty.sections
        if section.title == "标准保修期限"
    )

    assert "24 个月" in standard_warranty.content
