from datetime import date
from typing import Any

from business.nl2sql import NL2SQLGenerator


class FakeResponse:
    def __init__(self, output_text: str) -> None:
        self.output_text = output_text


class FakeGateway:
    def __init__(self, output_text: str) -> None:
        self.output_text = output_text
        self.calls: list[dict[str, Any]] = []

    def create_response(
        self,
        **kwargs: Any,
    ) -> FakeResponse:
        self.calls.append(kwargs)
        return FakeResponse(self.output_text)


def test_nl2sql_generator_uses_business_schema() -> None:
    gateway = FakeGateway(
        """
        SELECT p.product_name
        FROM products AS p
        LIMIT 1
        """.strip()
    )

    generator = NL2SQLGenerator(gateway)

    sql = generator.generate(
        "Which product should I inspect?",
        current_date=date(2026, 9, 13),
    )

    assert sql.startswith("SELECT")

    model_input = gateway.calls[0]["input"]

    assert "Current date: 2026-09-13" in model_input
    assert "products(" in model_input
    assert "customers(" in model_input
    assert "orders(" in model_input
    assert "order_items(" in model_input

    assert (
        "order_items.quantity"
        in model_input
    )
    assert (
        "status = 'completed'"
        in model_input
    )