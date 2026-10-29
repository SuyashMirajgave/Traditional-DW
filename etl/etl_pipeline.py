import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

SOURCE_DB = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("SOURCE_DB", "retail_source"),
    "user": os.getenv("DB_USER", "dwuser"),
    "password": os.getenv("DB_PASSWORD", ""),
}

WAREHOUSE_DB = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("WAREHOUSE_DB", "retail_warehouse"),
    "user": os.getenv("DB_USER", "dwuser"),
    "password": os.getenv("DB_PASSWORD", ""),
}



def extract_source_data():
    connection = psycopg2.connect(**SOURCE_DB)

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT product_id, product_name, category
                FROM products
                ORDER BY product_id;
            """)
            products = cursor.fetchall() 

            cursor.execute("""
                SELECT region_id, region_name, state_name
                FROM regions
                ORDER BY region_id;
            """)
            regions = cursor.fetchall()

            cursor.execute("""
                SELECT order_id, order_date, product_id,
                       region_id, quantity, unit_price
                FROM sales_orders
                ORDER BY order_id;
            """)
            sales = cursor.fetchall()

        return products, regions, sales

    finally:
        connection.close()


def load_warehouse(products, regions, sales):
    connection = psycopg2.connect(**WAREHOUSE_DB)

    try:
        with connection:
            with connection.cursor() as cursor:

                # Load product dimension
                cursor.executemany("""
                    INSERT INTO dim_product
                        (source_product_id, product_name, category)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (source_product_id)
                    DO UPDATE SET
                        product_name = EXCLUDED.product_name,
                        category = EXCLUDED.category;
                """, products)

                # Load region dimension
                cursor.executemany("""
                    INSERT INTO dim_region
                        (source_region_id, region_name, state_name)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (source_region_id)
                    DO UPDATE SET
                        region_name = EXCLUDED.region_name,
                        state_name = EXCLUDED.state_name;
                """, regions)

                # Load date dimension
                dates = sorted({sale[1] for sale in sales})

                for sale_date in dates:
                    date_key = int(sale_date.strftime("%Y%m%d"))

                    cursor.execute("""
                        INSERT INTO dim_date (
                            date_key, full_date, day_number,
                            month_number, month_name,
                            quarter_number, year_number
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (date_key)
                        DO UPDATE SET full_date = EXCLUDED.full_date;
                    """, (
                        date_key,
                        sale_date,
                        sale_date.day,
                        sale_date.month,
                        sale_date.strftime("%B"),
                        (sale_date.month - 1) // 3 + 1,
                        sale_date.year,
                    ))

                # Load sales fact table
                for sale in sales:
                    order_id, order_date, product_id, region_id, quantity, unit_price = sale

                    cursor.execute("""
                        SELECT product_key
                        FROM dim_product
                        WHERE source_product_id = %s;
                    """, (product_id,))
                    product_key = cursor.fetchone()[0]

                    cursor.execute("""
                        SELECT region_key
                        FROM dim_region
                        WHERE source_region_id = %s;
                    """, (region_id,))
                    region_key = cursor.fetchone()[0]

                    date_key = int(order_date.strftime("%Y%m%d"))
                    sales_amount = quantity * unit_price

                    cursor.execute("""
                        INSERT INTO fact_sales (
                            order_id, date_key, region_key,
                            product_key, quantity, unit_price,
                            sales_amount
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (order_id)
                        DO UPDATE SET
                            date_key = EXCLUDED.date_key,
                            region_key = EXCLUDED.region_key,
                            product_key = EXCLUDED.product_key,
                            quantity = EXCLUDED.quantity,
                            unit_price = EXCLUDED.unit_price,
                            sales_amount = EXCLUDED.sales_amount;
                    """, (
                        order_id,
                        date_key,
                        region_key,
                        product_key,
                        quantity,
                        unit_price,
                        sales_amount,
                    ))

        print("ETL pipeline completed successfully!")
        print(f"Products loaded: {len(products)}")
        print(f"Regions loaded: {len(regions)}")
        print(f"Sales records loaded: {len(sales)}")

    finally:
        connection.close()


def main():
    print("Extracting data from source database...")
    products, regions, sales = extract_source_data()

    print("Loading data into the warehouse...")
    load_warehouse(products, regions, sales)


if __name__ == "__main__":
    main()