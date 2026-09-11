from uuid import uuid4

from fastapi import APIRouter, Depends

from agent.context import AgentContext
from agent.graph import agent_graph
from apps.api.dependencies import (
    get_database,
    get_model_gateway,
)
from apps.api.schemas.chat import (
    ChatRequest,
    ChatResponse,
)
from models.gateway import ModelGateway
from storage.database import Database


router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    gateway: ModelGateway = Depends(get_model_gateway),
    database: Database = Depends(get_database),
) -> ChatResponse:
    request_id = uuid4().hex

    result = agent_graph.invoke(
        {
            "request_id": request_id,
            "user_message": request.message,
        },
        context=AgentContext(
            gateway=gateway,
            database=database,
        ),
    )

    return ChatResponse(
        request_id=request_id,
        answer=result["final_answer"],
        trace=result["trace"],
    )
