from datetime import date, timedelta
from decimal import Decimal
from random import Random

from sqlalchemy import create_engine, text

from settings import get_settings


REGIONS = ("North", "South", "East", "West")
SEGMENTS = ("SMB", "Mid-Market", "Enterprise")
CHANNELS = ("direct", "partner", "online")
ORDERS_PER_MONTH = 120


def next_month(year: int, month: int) -> tuple[int, int]:
    if month == 12:
        return year + 1, 1
    return year, month + 1


def main() -> None:
    rng = Random(42)
    engine = create_engine(get_settings().database_url)

    with engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE TABLE order_items, orders, customers "
                "RESTART IDENTITY"
            )
        )

        customers_by_region: dict[str, list[dict[str, object]]] = {
            region: [] for region in REGIONS
        }

        for region in REGIONS:
            for index in range(20):
                segment = SEGMENTS[index % len(SEGMENTS)]

                customer_id = connection.execute(
                    text(
                        """
                        INSERT INTO customers (
                            customer_name,
                            region,
                            segment
                        )
                        VALUES (
                            :customer_name,
                            :region,
                            :segment
                        )
                        RETURNING customer_id
                        """
                    ),
                    {
                        "customer_name": (
                            f"{region} Manufacturing {index + 1:02d}"
                        ),
                        "region": region,
                        "segment": segment,
                    },
                ).scalar_one()

                customers_by_region[region].append(
                    {
                        "customer_id": customer_id,
                        "segment": segment,
                    }
                )

        products = connection.execute(
            text(
                """
                SELECT product_id, product_name, unit_price
                FROM products
                WHERE active = TRUE
                ORDER BY product_id
                """
            )
        ).mappings().all()

        year, month = 2025, 1

        for _ in range(20):
            first_day = date(year, month, 1)
            next_year, next_month_value = next_month(year, month)
            next_first_day = date(
                next_year,
                next_month_value,
                1,
            )
            days_in_month = (
                next_first_day - first_day
            ).days

            region_weights = [25, 25, 25, 25]

            # Intentional synthetic pattern:
            # South-region demand drops in 2026 Q2.
            if year == 2026 and month in (4, 5, 6):
                region_weights = [30, 10, 30, 30]

            for _ in range(ORDERS_PER_MONTH):
                region = rng.choices(
                    REGIONS,
                    weights=region_weights,
                    k=1,
                )[0]

                customer = rng.choice(
                    customers_by_region[region]
                )

                order_date = first_day + timedelta(
                    days=rng.randrange(days_in_month)
                )

                if order_date >= date(2026, 7, 1):
                    status = rng.choices(
                        ("completed", "cancelled", "pending"),
                        weights=(86, 8, 6),
                        k=1,
                    )[0]
                else:
                    status = rng.choices(
                        ("completed", "cancelled"),
                        weights=(92, 8),
                        k=1,
                    )[0]

                order_id = connection.execute(
                    text(
                        """
                        INSERT INTO orders (
                            customer_id,
                            order_date,
                            status,
                            sales_channel
                        )
                        VALUES (
                            :customer_id,
                            :order_date,
                            :status,
                            :sales_channel
                        )
                        RETURNING order_id
                        """
                    ),
                    {
                        "customer_id": customer["customer_id"],
                        "order_date": order_date,
                        "status": status,
                        "sales_channel": rng.choice(CHANNELS),
                    },
                ).scalar_one()

                line_items = []
                used_product_ids: set[int] = set()

                for _ in range(rng.randint(1, 3)):
                    available_products = [
                        product
                        for product in products
                        if product["product_id"]
                        not in used_product_ids
                    ]

                    product = rng.choice(
                        available_products
                    )

                    used_product_ids.add(
                        product["product_id"]
                    )

                    segment = customer["segment"]

                    if segment == "Enterprise":
                        quantity = rng.randint(4, 10)
                    elif segment == "Mid-Market":
                        quantity = rng.randint(2, 6)
                    else:
                        quantity = rng.randint(1, 3)

                    catalog_price = Decimal(
                        product["unit_price"]
                    )

                    price_factor = Decimal(
                        str(
                            rng.choice(
                                (
                                    0.98,
                                    1.00,
                                    1.00,
                                    1.00,
                                    1.02,
                                )
                            )
                        )
                    )

                    unit_price = (
                        catalog_price * price_factor
                    ).quantize(Decimal("0.01"))

                    discount = Decimal(
                        str(
                            rng.choice(
                                (
                                    0,
                                    0,
                                    0.05,
                                    0.10,
                                    0.15,
                                )
                            )
                        )
                    )

                    line_items.append(
                        {
                            "order_id": order_id,
                            "product_id": (
                                product["product_id"]
                            ),
                            "quantity": quantity,
                            "unit_price": unit_price,
                            "discount": discount,
                        }
                    )

                connection.execute(
                    text(
                        """
                        INSERT INTO order_items (
                            order_id,
                            product_id,
                            quantity,
                            unit_price,
                            discount
                        )
                        VALUES (
                            :order_id,
                            :product_id,
                            :quantity,
                            :unit_price,
                            :discount
                        )
                        """
                    ),
                    line_items,
                )
            year, month = next_year, next_month_value

    print("Seeded business data successfully.")


if __name__ == "__main__":
    main()