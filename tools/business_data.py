from typing import Any

from storage.database import Database


PRODUCT_INFO_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_product_info",
        "description": (
            "Retrieve basic product catalog information from the enterprise "
            "product database."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "product_name": {
                    "type": "string",
                    "description": "Product name such as X100, X200, or X300.",
                }
            },
            "required": ["product_name"],
            "additionalProperties": False,
        },
    },
}


def get_product_info(
    database: Database,
    product_name: str,
) -> dict[str, Any]:
    product = database.get_product_info(product_name)

    if product is None:
        return {
            "found": False,
            "product_name": product_name,
        }

    return {
        "found": True,
        "product": product,
    }
