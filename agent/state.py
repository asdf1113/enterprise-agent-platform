from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    request_id: str
    user_message: str

    conversation: list[dict[str, Any]]

    pending_tool_calls: list[dict[str, Any]]
    tool_results: list[dict[str, Any]]

    tool_rounds: int

    final_answer: str | None

    trace: list[dict[str, Any]]
    
    citations: list[dict]
