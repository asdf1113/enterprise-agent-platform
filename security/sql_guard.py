import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError

from business.schema import ALLOWED_BUSINESS_TABLES


class SQLValidationError(ValueError):
    pass


class SQLGuard:
    def __init__(self, max_rows: int = 100) -> None:
        self.max_rows = max_rows

    def validate(self, sql: str) -> str:
        try:
            statements = sqlglot.parse(
                sql,
                read="postgres",
            )
        except ParseError as exc:
            raise SQLValidationError(
                "Invalid SQL syntax"
            ) from exc

        if len(statements) != 1:
            raise SQLValidationError(
                "Exactly one SQL statement is allowed"
            )

        statement = statements[0]

        if not isinstance(statement, exp.Query):
            raise SQLValidationError(
                "Only read-only queries are allowed"
            )

        forbidden_types = (
            exp.Insert,
            exp.Update,
            exp.Delete,
            exp.Create,
            exp.Drop,
            exp.Alter,
            exp.Merge,
        )

        for forbidden_type in forbidden_types:
            if statement.find(forbidden_type):
                raise SQLValidationError(
                    "Write or DDL operations are not allowed"
                )

        cte_names = {
            cte.alias_or_name.lower()
            for cte in statement.find_all(exp.CTE)
        }

        referenced_tables: set[str] = set()

        for table in statement.find_all(exp.Table):
            table_name = table.name.lower()

            # CTE names are temporary query aliases,
            # not physical database tables.
            if (
                not table.db
                and table_name in cte_names
            ):
                continue

            if table.catalog:
                raise SQLValidationError(
                    "Cross-database access is not allowed"
                )

            if table.db and table.db.lower() != "public":
                raise SQLValidationError(
                    "Only the public schema is allowed"
                )

            if table_name not in ALLOWED_BUSINESS_TABLES:
                raise SQLValidationError(
                    f"Table is not allowed: {table_name}"
                )

            referenced_tables.add(table_name)

        if not referenced_tables:
            raise SQLValidationError(
                "Query must reference an allowed business table"
            )

        normalized_sql = statement.sql(
            dialect="postgres"
        )

        return (
            "SELECT * FROM (\n"
            f"{normalized_sql}\n"
            ") AS guarded_query\n"
            f"LIMIT {self.max_rows}"
        )