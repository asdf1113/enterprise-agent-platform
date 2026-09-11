from typing import Any

from openai import OpenAI
from openai.types.responses import Response

from settings import Settings


class ModelGateway:
    def __init__(self, settings: Settings) -> None:
        if not settings.model_name:
            raise ValueError("MODEL_NAME must be configured")

        if not settings.model_api_key:
            raise ValueError("MODEL_API_KEY must be configured")

        client_args: dict[str, Any] = {
            "api_key": settings.model_api_key,
        }

        if settings.model_base_url:
            client_args["base_url"] = settings.model_base_url

        self.client = OpenAI(**client_args)
        self.model_name = settings.model_name

    def create_response(
        self,
        *,
        input: Any,
        instructions: str,
        tools: list[dict[str, Any]] | None = None,
    ) -> Response:
        request: dict[str, Any] = {
            "model": self.model_name,
            "input": input,
            "instructions": instructions,
        }

        if tools is not None:
            request["tools"] = tools
            request["tool_choice"] = "auto"

        return self.client.responses.create(**request)