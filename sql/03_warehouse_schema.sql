
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE UNIQUE NOT NULL,
    day_number INTEGER NOT NULL,
    month_number INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    quarter_number INTEGER NOT NULL,
    year_number INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_region (
    region_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_region_id INTEGER UNIQUE NOT NULL,
    region_name VARCHAR(50) NOT NULL,
    state_name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_product (
    product_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_product_id INTEGER UNIQUE NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_sales (
    sales_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id INTEGER UNIQUE NOT NULL,
    date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    region_key INTEGER NOT NULL REFERENCES dim_region(region_key),
    product_key INTEGER NOT NULL REFERENCES dim_product(product_key),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    sales_amount NUMERIC(12, 2) NOT NULL
);
