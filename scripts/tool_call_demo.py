import json
from typing import Any

from models.gateway import ModelGateway
from settings import get_settings
from storage.database import Database
from tools.business_data import (
    PRODUCT_INFO_TOOL_SCHEMA,
    get_product_info,
)


INSTRUCTIONS = """
You are an enterprise assistant.

For product catalog facts, use the provided enterprise tool instead of guessing.
After receiving tool results, answer the user concisely in Chinese.
"""


def main() -> None:
    settings = get_settings()

    gateway = ModelGateway(settings)
    database = Database(settings)

    user_request = "请查询 X999 的产品类别、价格和简介。"

    conversation: list[Any] = [
        {
            "role": "user",
            "content": user_request,
        }
    ]

    print("=== user ===")
    print(user_request)

    response = gateway.create_response(
        input=conversation,
        instructions=INSTRUCTIONS,
        tools=[PRODUCT_INFO_TOOL_SCHEMA],
    )

    print("\n=== first model response ===")
    print("response_id:", response.id)
    print("output types:", [item.type for item in response.output])

    tool_calls = [
        item
        for item in response.output
        if item.type == "function_call"
    ]

    if not tool_calls:
        raise RuntimeError(
            f"Expected a function call, got: {response.output_text!r}"
        )

    # Stateless Responses API:
    # keep the model's previous output in our local conversation state.
    conversation.extend(
        item.model_dump(mode="json", exclude_none=True)
        for item in response.output
    )

    for tool_call in tool_calls:
        print("\n=== function call ===")
        print("call_id:", tool_call.call_id)
        print("name:", tool_call.name)
        print("arguments:", tool_call.arguments)

        if tool_call.name != "get_product_info":
            raise ValueError(f"Unknown tool: {tool_call.name}")

        arguments = json.loads(tool_call.arguments)

        result = get_product_info(
            database,
            product_name=arguments["product_name"],
        )

        print("\n=== local tool result ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

        conversation.append(
            {
                "type": "function_call_output",
                "call_id": tool_call.call_id,
                "output": json.dumps(
                    result,
                    ensure_ascii=False,
                ),
            }
        )

    final_response = gateway.create_response(
        input=conversation,
        instructions=INSTRUCTIONS,
    )

    print("\n=== final model answer ===")
    print(final_response.output_text)


if __name__ == "__main__":
    main()