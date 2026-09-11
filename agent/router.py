from typing import Literal

from agent.state import AgentState


def route_after_model(
    state: AgentState,
) -> Literal["tool", "end"]:
    if state.get("pending_tool_calls"):
        return "tool"

    return "end"
