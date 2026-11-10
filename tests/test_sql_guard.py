import pytest

from security.sql_guard import (
    SQLGuard,
    SQLValidationError,
)


def test_allows_business_select() -> None:
    guard = SQLGuard(max_rows=100)

    sql = guard.validate(
        """
        SELECT product_name, unit_price
        FROM products
        WHERE active = TRUE
        """
    )

    assert "FROM products" in sql
    assert "LIMIT 100" in sql


def test_allows_join_query() -> None:
    guard = SQLGuard()

    sql = guard.validate(
        """
        SELECT c.region, COUNT(*)
        FROM orders AS o
        JOIN customers AS c
          ON c.customer_id = o.customer_id
        GROUP BY c.region
        """
    )

    assert "orders" in sql
    assert "customers" in sql


def test_allows_cte() -> None:
    guard = SQLGuard()

    sql = guard.validate(
        """
        WITH completed_orders AS (
            SELECT order_id
            FROM orders
            WHERE status = 'completed'
        )
        SELECT COUNT(*)
        FROM completed_orders
        """
    )

    assert "completed_orders" in sql


def test_rejects_update() -> None:
    guard = SQLGuard()

    with pytest.raises(SQLValidationError):
        guard.validate(
            "UPDATE products SET unit_price = 0"
        )


def test_rejects_multiple_statements() -> None:
    guard = SQLGuard()

    with pytest.raises(SQLValidationError):
        guard.validate(
            """
            SELECT * FROM products;
            DELETE FROM orders;
            """
        )


def test_rejects_unknown_table() -> None:
    guard = SQLGuard()

    with pytest.raises(SQLValidationError):
        guard.validate(
            "SELECT * FROM knowledge_chunks"
        )


def test_rejects_system_schema() -> None:
    guard = SQLGuard()

    with pytest.raises(SQLValidationError):
        guard.validate(
            "SELECT * FROM pg_catalog.pg_tables"
        )