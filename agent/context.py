from dataclasses import dataclass

from models.gateway import ModelGateway
from storage.database import Database


@dataclass(frozen=True)
class AgentContext:
    gateway: ModelGateway
    database: Database
