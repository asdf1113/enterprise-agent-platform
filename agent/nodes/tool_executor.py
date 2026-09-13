import json

from langgraph.runtime import Runtime

from agent.context import AgentContext
from agent.state import AgentState
from tools.business_data import get_product_info
from tools.knowledge import knowledge_search


def tool_executor_node(
    state: AgentState,
    runtime: Runtime[AgentContext],
) -> dict:
    function_outputs = []
    tool_results = [
        *state.get("tool_results", []),
    ]
    citations = [
        *state.get("citations", []),
    ]
    executed_tools = []

    for tool_call in state["pending_tool_calls"]:
        tool_name = tool_call["name"]
        arguments = json.loads(tool_call["arguments"])

        if tool_name == "get_product_info":        
            result = get_product_info(
                runtime.context.database,
                product_name=arguments["product_name"],
            )
        elif tool_name == "knowledge_search":
            factory = (
                runtime.context
                .knowledge_retriever_factory
            )

            if factory is None:
                raise RuntimeError(
                    "Knowledge retriever is not configured"
                )

            result = knowledge_search(
                factory(),
                query=arguments["query"],
                role=runtime.context.user_role,
                current_date=runtime.context.current_date,
                as_of_date=arguments["as_of_date"],
            )
            
            existing_citations = {
                (
                    item["document_id"],
                    item["version"],
                    item["section_title"],
                )
                for item in citations
            }

            for item in result["results"]:
                key = (
                    item["document_id"],
                    item["version"],
                    item["section_title"],
                )

                if key in existing_citations:
                    continue

                citations.append(
                    {
                        "citation_id": item["citation_id"],
                        "document_id": item["document_id"],
                        "document_name": item["document_name"],
                        "version": item["version"],
                        "section_title": item["section_title"],
                        "source_path": item["source_path"],
                    }
                )

                existing_citations.add(key)

        else:
            raise ValueError(
                f"Unsupported tool: {tool_name}"
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
        "citations": citations,
    }
