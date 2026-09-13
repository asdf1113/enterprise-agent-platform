ALLOWED_BUSINESS_TABLES = frozenset(
    {
        "products",
        "customers",
        "orders",
        "order_items",
    }
)


BUSINESS_SCHEMA = """
products(
    product_id BIGINT PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    unit_price NUMERIC,
    description TEXT,
    active BOOLEAN
)

customers(
    customer_id BIGINT PRIMARY KEY,
    customer_name TEXT,
    region TEXT,
    segment TEXT
)

orders(
    order_id BIGINT PRIMARY KEY,
    customer_id BIGINT,
    order_date DATE,
    status TEXT,
    sales_channel TEXT
)

order_items(
    order_item_id BIGINT PRIMARY KEY,
    order_id BIGINT,
    product_id BIGINT,
    quantity INTEGER,
    unit_price NUMERIC,
    discount NUMERIC
)

Relationships:
customers.customer_id = orders.customer_id
orders.order_id = order_items.order_id
products.product_id = order_items.product_id
""".strip()


BUSINESS_SEMANTICS = """
Business rules:

- Revenue means:
  order_items.quantity
  * order_items.unit_price
  * (1 - order_items.discount).

- Only orders with status = 'completed'
  count as realized sales or realized revenue.

- Sales quantity means the sum of
  order_items.quantity from completed orders.

- Customer region and segment come from
  the customers table.

- Sales dates use orders.order_date.

- products.unit_price is the current catalog price.

- order_items.unit_price is the historical transaction
  price for that order and must be used for revenue analysis.

Known categorical values:

customers.region:
North, South, East, West

customers.segment:
SMB, Mid-Market, Enterprise

orders.status:
completed, cancelled, pending

orders.sales_channel:
direct, partner, online
""".strip()


def build_business_schema_context() -> str:
    return (
        "Available business database schema:\n\n"
        f"{BUSINESS_SCHEMA}\n\n"
        f"{BUSINESS_SEMANTICS}"
    )