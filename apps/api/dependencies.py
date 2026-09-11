from functools import lru_cache

from models.gateway import ModelGateway
from settings import get_settings
from storage.database import Database


@lru_cache
def get_model_gateway() -> ModelGateway:
    return ModelGateway(get_settings())


@lru_cache
def get_database() -> Database:
    return Database(get_settings())
