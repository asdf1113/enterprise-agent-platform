from typing import Literal

from agent.state import AgentState


MAX_TOOL_ROUNDS = 4


def route_after_model(
    state: AgentState,
) -> Literal["tool", "end"]:
    if not state.get("pending_tool_calls"):
        return "end"

    if state.get("tool_rounds", 0) >= MAX_TOOL_ROUNDS:
        raise RuntimeError(
            f"Maximum tool rounds exceeded: {MAX_TOOL_ROUNDS}"
        )

    return "tool"