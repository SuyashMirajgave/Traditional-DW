
INSERT INTO products (product_id, product_name, category, unit_price) VALUES
(1, 'Laptop', 'Electronics', 55000.00),
(2, 'Wireless Mouse', 'Accessories', 800.00),
(3, 'Keyboard', 'Accessories', 1500.00),
(4, 'Monitor', 'Electronics', 12000.00),
(5, 'Office Chair', 'Furniture', 8500.00);

INSERT INTO regions (region_id, region_name, state_name) VALUES
(1, 'West', 'Maharashtra'),
(2, 'South', 'Karnataka'),
(3, 'North', 'Delhi'),
(4, 'East', 'West Bengal');

INSERT INTO sales_orders
(order_id, order_date, product_id, region_id, quantity, unit_price)
VALUES
(1001, '2026-01-05', 1, 1, 2, 55000.00),
(1002, '2026-01-08', 2, 2, 5, 800.00),
(1003, '2026-01-12', 3, 1, 3, 1500.00),
(1004, '2026-02-03', 4, 3, 2, 12000.00),
(1005, '2026-02-10', 5, 4, 1, 8500.00),
(1006, '2026-02-15', 1, 2, 1, 55000.00),
(1007, '2026-03-01', 2, 1, 10, 800.00),
(1008, '2026-03-06', 4, 3, 3, 12000.00),
(1009, '2026-03-11', 3, 4, 4, 1500.00),
(1010, '2026-03-20', 5, 1, 2, 8500.00);
