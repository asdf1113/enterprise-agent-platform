from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from settings import Settings


class Database:
    def __init__(self, settings: Settings) -> None:
        self.engine: Engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
        )

    def get_product_info(self, product_name: str) -> dict[str, Any] | None:
        statement = text(
            """
            SELECT
                product_id,
                product_name,
                category,
                unit_price,
                description,
                active
            FROM products
            WHERE lower(product_name) = lower(:product_name)
            LIMIT 1
            """
        )

        with self.engine.connect() as connection:
            row = connection.execute(
                statement,
                {"product_name": product_name},
            ).mappings().first()

        if row is None:
            return None

        return dict(row)
