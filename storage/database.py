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

    def execute_readonly_query(
        self,
        sql: str,
        *,
        timeout_ms: int = 3000,
    ) -> list[dict[str, Any]]:
        if timeout_ms <= 0:
            raise ValueError(
                "timeout_ms must be positive"
            )

        with self.engine.connect() as connection:
            with connection.begin():
                connection.exec_driver_sql(
                    "SET TRANSACTION READ ONLY"
                )

                connection.exec_driver_sql(
                    "SET LOCAL statement_timeout "
                    f"= {timeout_ms}"
                )

                rows = connection.execute(
                    text(sql)
                ).mappings().all()

        return [
            dict(row)
            for row in rows
        ]