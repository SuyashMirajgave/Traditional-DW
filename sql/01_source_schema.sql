
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS regions (
    region_id INTEGER PRIMARY KEY,
    region_name VARCHAR(50) NOT NULL,
    state_name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS sales_orders (
    order_id INTEGER PRIMARY KEY,
    order_date DATE NOT NULL,
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    region_id INTEGER NOT NULL REFERENCES regions(region_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL
);
