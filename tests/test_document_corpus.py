import json
from pathlib import Path


DOCUMENT_ROOT = Path("data/documents")
MANIFEST_PATH = DOCUMENT_ROOT / "manifest.json"


def load_manifest() -> list[dict]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_document_manifest_entries_are_valid() -> None:
    documents = load_manifest()

    assert len(documents) >= 5

    document_ids = {
        document["document_id"]
        for document in documents
    }

    assert len(document_ids) == len(documents)

    required_fields = {
        "document_id",
        "source_path",
        "document_name",
        "document_type",
        "department",
        "version",
        "effective_date",
        "product",
        "region",
        "allowed_roles",
    }

    for document in documents:
        assert required_fields <= document.keys()

        source = DOCUMENT_ROOT / document["source_path"]

        assert source.is_file()
        assert source.read_text(encoding="utf-8").strip()

        assert document["allowed_roles"]


def test_warranty_corpus_contains_version_conflict() -> None:
    documents = load_manifest()

    warranty_versions = {
        document["version"]
        for document in documents
        if document["document_id"].startswith(
            "warranty-policy-"
        )
    }

    assert {
        "2025",
        "2026",
    } <= warranty_versions
