from datetime import date

from rag.retriever import DenseKnowledgeRetriever
from settings import get_settings
from storage.database import Database


def test_retrieval_uses_latest_effective_version() -> None:
    store = DenseKnowledgeRetriever(
        Database(get_settings())
    )

    # A deterministic vector is enough for this test because
    # we only care about metadata eligibility, not ranking.
    embedding = [0.0] * 1024

    results_2025 = store.search(
        embedding,
        role="support",
        as_of_date=date(2025, 12, 31),
        product="X200",
        limit=20,
    )

    warranty_2025 = {
        result.document_id
        for result in results_2025
        if result.document_group == "warranty-policy"
    }

    assert warranty_2025 == {
        "warranty-policy-2025"
    }

    results_2026 = store.search(
        embedding,
        role="support",
        as_of_date=date(2026, 9, 12),
        product="X200",
        limit=20,
    )

    warranty_2026 = {
        result.document_id
        for result in results_2026
        if result.document_group == "warranty-policy"
    }

    assert warranty_2026 == {
        "warranty-policy-2026"
    }


def test_retrieval_enforces_role_acl() -> None:
    store = DenseKnowledgeRetriever(
        Database(get_settings())
    )

    embedding = [0.0] * 1024

    results = store.search(
        embedding,
        role="support",
        as_of_date=date(2026, 9, 12),
        limit=20,
    )

    assert all(
        result.document_type != "sales_policy"
        for result in results
    )
