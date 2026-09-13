from datetime import date

from rag.retriever import RetrievedChunk
from tools.knowledge import knowledge_search


class FakeKnowledgeRetriever:
    def __init__(self) -> None:
        self.last_call = None

    def search(
        self,
        query: str,
        *,
        role: str,
        as_of_date: date,
        product=None,
        region=None,
    ) -> list[RetrievedChunk]:
        self.last_call = {
            "query": query,
            "role": role,
            "as_of_date": as_of_date,
        }

        return [
            RetrievedChunk(
                chunk_id="warranty-policy-2026:0000",
                document_id="warranty-policy-2026",
                document_group="warranty-policy",
                document_name="产品售后保修政策（2026版）",
                document_type="after_sales",
                version="2026",
                effective_date=date(2026, 1, 1),
                product="all",
                region="all",
                source_path=(
                    "after_sales/warranty_policy_2026.md"
                ),
                section_title="标准保修期限",
                content="X200 标准保修期限为 24 个月。",
                dense_score=0.76,
                rerank_score=0.99,
            )
        ]


def test_knowledge_search_returns_structured_evidence() -> None:
    retriever = FakeKnowledgeRetriever()

    result = knowledge_search(
        retriever,
        query="X200 的标准保修期多久？",
        role="support",
        current_date=date(2026, 9, 12),
        as_of_date=None,
    )

    assert retriever.last_call == {
        "query": "X200 的标准保修期多久？",
        "role": "support",
        "as_of_date": date(2026, 9, 12),
    }

    assert result["count"] == 1
    assert result["results"][0]["citation_id"] == "K1"
    assert (
        result["results"][0]["document_id"]
        == "warranty-policy-2026"
    )
    assert "24 个月" in result["results"][0]["content"]


def test_knowledge_search_supports_historical_date() -> None:
    retriever = FakeKnowledgeRetriever()

    knowledge_search(
        retriever,
        query="2025 年 X200 的保修政策是什么？",
        role="support",
        current_date=date(2026, 9, 12),
        as_of_date="2025-12-31",
    )

    assert retriever.last_call["as_of_date"] == date(
        2025,
        12,
        31,
    )
