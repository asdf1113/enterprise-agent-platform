from datetime import date

from models.gateway import ModelGateway
from business.schema import build_business_schema_context


NL2SQL_INSTRUCTIONS = """
You translate natural-language business questions into PostgreSQL queries.

Generate exactly one read-only SQL query.

Rules:
- Return SQL only. Do not use Markdown code fences.
- Use only tables and columns provided in the business schema.
- Do not invent schema elements.
- Follow the provided business semantics exactly.
- Use PostgreSQL syntax.
- Generate only SELECT statements or WITH ... SELECT queries.
- Resolve relative dates using the provided current date.
""".strip()


class NL2SQLGenerator:
    def __init__(self, gateway: ModelGateway) -> None:
        self.gateway = gateway

    def generate(
        self,
        question: str,
        *,
        current_date: date,
    ) -> str:
        schema_context = build_business_schema_context()

        model_input = (
            f"Current date: {current_date.isoformat()}\n\n"
            f"{schema_context}\n\n"
            "Business question:\n"
            f"{question}"
        )

        response = self.gateway.create_response(
            input=model_input,
            instructions=NL2SQL_INSTRUCTIONS,
        )

        sql = response.output_text.strip()

        if not sql:
            raise ValueError("Model returned empty SQL")

        return sql