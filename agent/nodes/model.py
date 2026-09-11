from langgraph.runtime import Runtime

from agent.context import AgentContext
from agent.state import AgentState
from tools.business_data import PRODUCT_INFO_TOOL_SCHEMA


INSTRUCTIONS = """
You are an enterprise assistant.

For product catalog facts, use the provided enterprise tool instead of guessing.
After receiving tool results, answer the user concisely in Chinese.
"""


def model_node(
    state: AgentState,
    runtime: Runtime[AgentContext],
) -> dict:
    response = runtime.context.gateway.create_response(
        input=state["conversation"],
        instructions=INSTRUCTIONS,
        tools=[PRODUCT_INFO_TOOL_SCHEMA],
    )

    output_items = [
        item.model_dump(mode="json", exclude_none=True)
        for item in response.output
    ]

    tool_calls = [
        {
            "call_id": item.call_id,
            "name": item.name,
            "arguments": item.arguments,
        }
        for item in response.output
        if item.type == "function_call"
    ]

    trace = [
        *state.get("trace", []),
        {
            "node": "model",
            "event": "model_response",
            "response_id": response.id,
            "output_types": [item.type for item in response.output],
            "tool_names": [call["name"] for call in tool_calls],
        },
    ]

    update = {
        "conversation": [
            *state["conversation"],
            *output_items,
        ],
        "pending_tool_calls": tool_calls,
        "trace": trace,
    }

    if not tool_calls:
        update["final_answer"] = response.output_text.strip()

    return update
