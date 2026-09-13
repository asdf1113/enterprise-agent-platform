from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date

from models.gateway import ModelGateway
from rag.retriever import KnowledgeRetriever
from storage.database import Database



@dataclass(frozen=True)
class AgentContext:
    gateway: ModelGateway
    database: Database
    
    knowledge_retriever_factory: (
        Callable[[], KnowledgeRetriever] | None
    ) = None

    user_role: str = "support"
    current_date: date = field(
        default_factory=date.today
    )
