import json

from langgraph.runtime import Runtime

from agent.context import AgentContext
from agent.state import AgentState
from tools.business_data import get_product_info


def tool_executor_node(
    state: AgentState,
    runtime: Runtime[AgentContext],
) -> dict:
    function_outputs = []
    tool_results = [
        *state.get("tool_results", []),
    ]
    executed_tools = []

    for tool_call in state["pending_tool_calls"]:
        if tool_call["name"] != "get_product_info":
            raise ValueError(
                f"Unknown tool: {tool_call['name']}"
            )

        arguments = json.loads(tool_call["arguments"])

        result = get_product_info(
            runtime.context.database,
            product_name=arguments["product_name"],
        )

        function_outputs.append(
            {
                "type": "function_call_output",
                "call_id": tool_call["call_id"],
                "output": json.dumps(
                    result,
                    ensure_ascii=False,
                ),
            }
        )

        tool_results.append(
            {
                "name": tool_call["name"],
                "arguments": arguments,
                "result": result,
            }
        )

        executed_tools.append(tool_call["name"])

    return {
        "conversation": [
            *state["conversation"],
            *function_outputs,
        ],
        "pending_tool_calls": [],
        "tool_results": tool_results,
        "tool_rounds": state.get("tool_rounds", 0) + 1,
        "trace": [
            *state.get("trace", []),
            {
                "node": "tool_executor",
                "event": "tools_executed",
                "tools": executed_tools,
            },
        ],
    }
