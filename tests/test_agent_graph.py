import json
from decimal import Decimal
from typing import Any

import pytest
from datetime import date

from rag.retriever import RetrievedChunk
from agent.context import AgentContext
from agent.graph import agent_graph
from agent.router import MAX_TOOL_ROUNDS, route_after_model


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
                chunk_id=(
                    "warranty-policy-2026:0000"
                ),
                document_id=(
                    "warranty-policy-2026"
                ),
                document_group=(
                    "warranty-policy"
                ),
                document_name=(
                    "产品售后保修政策（2026版）"
                ),
                document_type="after_sales",
                version="2026",
                effective_date=date(
                    2026,
                    1,
                    1,
                ),
                product="all",
                region="all",
                source_path=(
                    "after_sales/"
                    "warranty_policy_2026.md"
                ),
                section_title="标准保修期限",
                content=(
                    "X200 标准保修期限为 24 个月。"
                ),
                dense_score=0.76,
                rerank_score=0.99,
            )
        ]

class FakeOutputItem:
    def __init__(
        self,
        item_type: str,
        **payload: Any,
    ) -> None:
        self.type = item_type

        for key, value in payload.items():
            setattr(self, key, value)

    def model_dump(
        self,
        mode: str = "python",
        exclude_none: bool = False,
    ) -> dict[str, Any]:
        data = {
            "type": self.type,
            **{
                key: value
                for key, value in self.__dict__.items()
                if key != "type"
            },
        }

        if exclude_none:
            data = {
                key: value
                for key, value in data.items()
                if value is not None
            }

        return data


class FakeResponse:
    def __init__(
        self,
        response_id: str,
        output: list[FakeOutputItem],
        output_text: str,
    ) -> None:
        self.id = response_id
        self.output = output
        self.output_text = output_text


class FakeGateway:
    def __init__(
        self,
        responses: list[FakeResponse],
    ) -> None:
        self.responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    def create_response(
        self,
        **kwargs: Any,
    ) -> FakeResponse:
        self.calls.append(kwargs)
        return self.responses.pop(0)


class FakeDatabase:
    def get_product_info(
        self,
        product_name: str,
    ) -> dict[str, Any] | None:
        if product_name != "X200":
            return None

        return {
            "product_id": 2,
            "product_name": "X200",
            "category": "Industrial Controller",
            "unit_price": Decimal("6999.00"),
            "description": "Test product",
            "active": True,
        }


def test_agent_graph_executes_product_tool() -> None:
    gateway = FakeGateway(
        [
            FakeResponse(
                response_id="resp-1",
                output=[
                    FakeOutputItem("reasoning"),
                    FakeOutputItem(
                        "function_call",
                        call_id="call-1",
                        name="get_product_info",
                        arguments='{"product_name":"X200"}',
                    ),
                ],
                output_text="",
            ),
            FakeResponse(
                response_id="resp-2",
                output=[
                    FakeOutputItem("reasoning"),
                    FakeOutputItem("message"),
                ],
                output_text="X200 的价格为 6999 元。",
            ),
        ]
    )

    result = agent_graph.invoke(
        {
            "request_id": "request-1",
            "user_message": "查询 X200。",
        },
        context=AgentContext(
            gateway=gateway,
            database=FakeDatabase(),
        ),
    )

    assert result["final_answer"] == "X200 的价格为 6999 元。"

    assert [
        event["node"]
        for event in result["trace"]
    ] == [
        "request_parser",
        "model",
        "tool_executor",
        "model",
    ]

    assert result["tool_rounds"] == 1

    assert result["tool_results"][0]["name"] == "get_product_info"
    assert (
        result["tool_results"][0]["arguments"]["product_name"]
        == "X200"
    )
    assert (
        result["tool_results"][0]["result"]["product"]["product_name"]
        == "X200"
    )

    second_model_input = gateway.calls[1]["input"]

    assert any(
        item.get("type") == "function_call_output"
        and item.get("call_id") == "call-1"
        for item in second_model_input
    )


def test_agent_graph_skips_tool_when_not_needed() -> None:
    gateway = FakeGateway(
        [
            FakeResponse(
                response_id="resp-1",
                output=[
                    FakeOutputItem("reasoning"),
                    FakeOutputItem("message"),
                ],
                output_text="你好！",
            )
        ]
    )

    result = agent_graph.invoke(
        {
            "request_id": "request-2",
            "user_message": "你好",
        },
        context=AgentContext(
            gateway=gateway,
            database=FakeDatabase(),
        ),
    )

    assert result["final_answer"] == "你好！"

    assert [
        event["node"]
        for event in result["trace"]
    ] == [
        "request_parser",
        "model",
    ]

    assert result["tool_results"] == []
    assert result["tool_rounds"] == 0
    assert len(gateway.calls) == 1


def test_router_rejects_excessive_tool_rounds() -> None:
    with pytest.raises(
        RuntimeError,
        match="Maximum tool rounds exceeded",
    ):
        route_after_model(
            {
                "pending_tool_calls": [
                    {
                        "call_id": "call-1",
                        "name": "get_product_info",
                        "arguments": "{}",
                    }
                ],
                "tool_rounds": MAX_TOOL_ROUNDS,
            }
        )

def test_agent_graph_executes_knowledge_search() -> None:
    fake_retriever = FakeKnowledgeRetriever()

    gateway = FakeGateway(
        [
            FakeResponse(
                response_id="resp-knowledge-1",
                output=[
                    FakeOutputItem(
                        "reasoning",
                    ),
                    FakeOutputItem(
                        "function_call",
                        call_id="call-knowledge-1",
                        name="knowledge_search",
                        arguments=json.dumps(
                            {
                                "query": (
                                    "X200 的标准保修期多久？"
                                ),
                                "as_of_date": None,
                            },
                            ensure_ascii=False,
                        ),
                    ),
                ],
                output_text="",
            ),
            FakeResponse(
                response_id="resp-knowledge-2",
                output=[
                    FakeOutputItem(
                        "reasoning",
                    ),
                    FakeOutputItem(
                        "message",
                    ),
                ],
                output_text=(
                    "X200 的标准保修期为 "
                    "24 个月。[K1]"
                ),
            ),
        ]
    )

    context = AgentContext(
        gateway=gateway,
        database=FakeDatabase(),
        knowledge_retriever_factory=(
            lambda: fake_retriever
        ),
        user_role="support",
        current_date=date(
            2026,
            9,
            12,
        ),
    )

    result = agent_graph.invoke(
        {
            "request_id": "req-knowledge-1",
            "user_message": (
                "X200 的标准保修期多久？"
            ),
        },
        context=context,
    )

    assert result["tool_rounds"] == 1

    assert fake_retriever.last_call == {
        "query": "X200 的标准保修期多久？",
        "role": "support",
        "as_of_date": date(2026, 9, 12),
    }

    assert (
        result["final_answer"]
        == "X200 的标准保修期为 24 个月。[K1]"
    )

    assert (
        result["citations"][0]["citation_id"]
        == "K1"
    )

    assert (
        result["citations"][0]["document_id"]
        == "warranty-policy-2026"
    )

    assert [
        item["node"]
        for item in result["trace"]
    ] == [
        "request_parser",
        "model",
        "tool_executor",
        "model",
    ]

    second_model_input = gateway.calls[1]["input"]

    assert any(
        item.get("type")
        == "function_call_output"
        and item.get("call_id")
        == "call-knowledge-1"
        for item in second_model_input
    )