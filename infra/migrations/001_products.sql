CREATE TABLE IF NOT EXISTS products (
    product_id BIGSERIAL PRIMARY KEY,
    product_name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    unit_price NUMERIC(12, 2) NOT NULL,
    description TEXT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE
);

INSERT INTO products (
    product_name,
    category,
    unit_price,
    description
)
VALUES
    (
        'X100',
        'Industrial Controller',
        3999.00,
        'Entry-level industrial controller for standard automation workloads.'
    ),
    (
        'X200',
        'Industrial Controller',
        6999.00,
        'Mid-range industrial controller designed for multi-device automation and production-line control.'
    ),
    (
        'X300',
        'Industrial Controller',
        10999.00,
        'High-performance industrial controller for complex real-time industrial workloads.'
    )
ON CONFLICT (product_name) DO NOTHING;
