from uuid import uuid4

from fastapi import APIRouter, Depends

from agent.context import AgentContext
from agent.graph import agent_graph
from apps.api.dependencies import (
    get_database,
    get_knowledge_retriever,
    get_model_gateway,
)
from apps.api.schemas.chat import (
    ChatRequest,
    ChatResponse,
)
from models.gateway import ModelGateway
from storage.database import Database

from datetime import date

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
                # 注意：这里传函数，不调用。不是get_knowledge_retriever()，后者会让每次/chat都立即触发模型加载
            knowledge_retriever_factory=get_knowledge_retriever,

            user_role=request.user_role,
            current_date=date.today(),
        ),
    )

    return ChatResponse(
        request_id=request_id,
        answer=result["final_answer"],
        citations=result.get(
            "citations",
            [],
        ),
        trace=result["trace"],
    )
