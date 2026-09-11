from langgraph.graph import END, START, StateGraph

from agent.context import AgentContext
from agent.nodes.model import model_node
from agent.nodes.request_parser import request_parser
from agent.nodes.tool_executor import tool_executor_node
from agent.router import route_after_model
from agent.state import AgentState


def build_agent_graph():
    builder = StateGraph(
        AgentState,
        context_schema=AgentContext,
    )

    builder.add_node(
        "request_parser",
        request_parser,
    )
    builder.add_node(
        "model",
        model_node,
    )
    builder.add_node(
        "tool_executor",
        tool_executor_node,
    )

    builder.add_edge(
        START,
        "request_parser",
    )
    builder.add_edge(
        "request_parser",
        "model",
    )

    builder.add_conditional_edges(
        "model",
        route_after_model,
        {
            "tool": "tool_executor",
            "end": END,
        },
    )

    builder.add_edge(
        "tool_executor",
        "model",
    )

    return builder.compile()


agent_graph = build_agent_graph()
