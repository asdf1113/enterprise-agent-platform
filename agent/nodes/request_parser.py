from agent.state import AgentState


def request_parser(state: AgentState) -> dict:
    user_message = state["user_message"].strip()

    if not user_message:
        raise ValueError("user_message must not be empty")

    return {
        "conversation": [
            {
                "role": "user",
                "content": user_message,
            }
        ],
        "pending_tool_calls": [],
        "tool_results": [],
        "tool_rounds": 0,
        "final_answer": None,
        "trace": [
            {
                "node": "request_parser",
                "event": "request_parsed",
            }
        ],
        "citations": [],
    }
