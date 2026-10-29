
-- 1. Overall sales performance
SELECT
    COUNT(*) AS total_orders,
    SUM(quantity) AS total_units_sold,
    SUM(sales_amount) AS total_revenue,
    ROUND(AVG(sales_amount), 2) AS average_order_value
FROM fact_sales;


-- 2. Product-wise revenue
SELECT
    p.product_name,
    SUM(f.quantity) AS units_sold,
    SUM(f.sales_amount) AS revenue
FROM fact_sales f
JOIN dim_product p
    ON f.product_key = p.product_key
GROUP BY p.product_name
ORDER BY revenue DESC;


-- 3. Monthly revenue trend
SELECT
    d.year_number,
    d.month_number,
    d.month_name,
    SUM(f.sales_amount) AS monthly_revenue
FROM fact_sales f
JOIN dim_date d
    ON f.date_key = d.date_key
GROUP BY
    d.year_number,
    d.month_number,
    d.month_name
ORDER BY
    d.year_number,
    d.month_number;


-- 4. Region-wise revenue
SELECT
    r.region_name,
    r.state_name,
    SUM(f.sales_amount) AS revenue
FROM fact_sales f
JOIN dim_region r
    ON f.region_key = r.region_key
GROUP BY r.region_name, r.state_name
ORDER BY revenue DESC;


-- 5. Category-wise performance
SELECT
    p.category,
    SUM(f.quantity) AS units_sold,
    SUM(f.sales_amount) AS revenue
FROM fact_sales f
JOIN dim_product p
    ON f.product_key = p.product_key
GROUP BY p.category
ORDER BY revenue DESC;
