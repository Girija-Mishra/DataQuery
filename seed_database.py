import random
from datetime import date, timedelta

from sqlalchemy import text

from database import engine


random.seed(42)


def random_date(start, end):
    days = (end - start).days
    return start + timedelta(days=random.randint(0, days))


with engine.begin() as conn:

    # Clear existing tables if the script is run again
    conn.execute(text("DROP TABLE IF EXISTS order_items"))
    conn.execute(text("DROP TABLE IF EXISTS orders"))
    conn.execute(text("DROP TABLE IF EXISTS products"))
    conn.execute(text("DROP TABLE IF EXISTS customers"))
    conn.execute(text("DROP TABLE IF EXISTS employees"))
    conn.execute(text("DROP TABLE IF EXISTS departments"))
    conn.execute(text("DROP TABLE IF EXISTS suppliers"))
    conn.execute(text("DROP TABLE IF EXISTS regions"))

    # -------------------------
    # REGIONS
    # -------------------------
    conn.execute(text("""
        CREATE TABLE regions (
            region_id INT PRIMARY KEY,
            region_name VARCHAR(100),
            country VARCHAR(100)
        )
    """))

    regions = [
        (1, "North", "India"),
        (2, "South", "India"),
        (3, "East", "India"),
        (4, "West", "India"),
        (5, "Central", "India")
    ]

    for r in regions:
        conn.execute(
            text("""
                INSERT INTO regions
                VALUES (:id, :name, :country)
            """),
            {"id": r[0], "name": r[1], "country": r[2]}
        )

    # -------------------------
    # DEPARTMENTS
    # -------------------------
    conn.execute(text("""
        CREATE TABLE departments (
            department_id INT PRIMARY KEY,
            department_name VARCHAR(100)
        )
    """))

    departments = [
        (1, "Engineering"),
        (2, "Sales"),
        (3, "Marketing"),
        (4, "Finance"),
        (5, "Human Resources"),
        (6, "Operations")
    ]

    for d in departments:
        conn.execute(
            text("""
                INSERT INTO departments
                VALUES (:id, :name)
            """),
            {"id": d[0], "name": d[1]}
        )

    # -------------------------
    # SUPPLIERS
    # -------------------------
    conn.execute(text("""
        CREATE TABLE suppliers (
            supplier_id INT PRIMARY KEY,
            supplier_name VARCHAR(150),
            region_id INT,
            FOREIGN KEY (region_id) REFERENCES regions(region_id)
        )
    """))

    for i in range(1, 101):
        conn.execute(
            text("""
                INSERT INTO suppliers
                VALUES (:id, :name, :region)
            """),
            {
                "id": i,
                "name": f"Supplier {i}",
                "region": random.randint(1, 5)
            }
        )

    # -------------------------
    # CUSTOMERS
    # -------------------------
    conn.execute(text("""
        CREATE TABLE customers (
            customer_id INT PRIMARY KEY,
            customer_name VARCHAR(150),
            email VARCHAR(200),
            region_id INT,
            signup_date DATE,
            FOREIGN KEY (region_id) REFERENCES regions(region_id)
        )
    """))

    for i in range(1, 5001):
        conn.execute(
            text("""
                INSERT INTO customers
                VALUES (:id, :name, :email, :region, :signup)
            """),
            {
                "id": i,
                "name": f"Customer {i}",
                "email": f"customer{i}@example.com",
                "region": random.randint(1, 5),
                "signup": random_date(
                    date(2021, 1, 1),
                    date(2026, 1, 1)
                )
            }
        )

    # -------------------------
    # PRODUCTS
    # -------------------------
    conn.execute(text("""
        CREATE TABLE products (
            product_id INT PRIMARY KEY,
            product_name VARCHAR(150),
            category VARCHAR(100),
            price DECIMAL(10,2),
            supplier_id INT,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
        )
    """))

    categories = [
        "Electronics",
        "Furniture",
        "Clothing",
        "Books",
        "Sports",
        "Home",
        "Beauty",
        "Grocery"
    ]

    for i in range(1, 501):
        conn.execute(
            text("""
                INSERT INTO products
                VALUES (:id, :name, :category, :price, :supplier)
            """),
            {
                "id": i,
                "name": f"Product {i}",
                "category": random.choice(categories),
                "price": round(random.uniform(100, 100000), 2),
                "supplier": random.randint(1, 100)
            }
        )

    # -------------------------
    # EMPLOYEES
    # -------------------------
    conn.execute(text("""
        CREATE TABLE employees (
            employee_id INT PRIMARY KEY,
            employee_name VARCHAR(150),
            department_id INT,
            region_id INT,
            salary DECIMAL(12,2),
            hire_date DATE,
            FOREIGN KEY (department_id)
                REFERENCES departments(department_id),
            FOREIGN KEY (region_id)
                REFERENCES regions(region_id)
        )
    """))

    for i in range(1, 1001):
        conn.execute(
            text("""
                INSERT INTO employees
                VALUES (:id, :name, :department, :region, :salary, :hire)
            """),
            {
                "id": i,
                "name": f"Employee {i}",
                "department": random.randint(1, 6),
                "region": random.randint(1, 5),
                "salary": round(random.uniform(25000, 250000), 2),
                "hire": random_date(
                    date(2018, 1, 1),
                    date(2026, 1, 1)
                )
            }
        )

    # -------------------------
    # ORDERS
    # -------------------------
    conn.execute(text("""
        CREATE TABLE orders (
            order_id INT PRIMARY KEY,
            customer_id INT,
            order_date DATE,
            region_id INT,
            status VARCHAR(50),
            FOREIGN KEY (customer_id)
                REFERENCES customers(customer_id),
            FOREIGN KEY (region_id)
                REFERENCES regions(region_id)
        )
    """))

    statuses = ["Completed", "Pending", "Cancelled", "Shipped"]

    for i in range(1, 10001):
        conn.execute(
            text("""
                INSERT INTO orders
                VALUES (:id, :customer, :date, :region, :status)
            """),
            {
                "id": i,
                "customer": random.randint(1, 5000),
                "date": random_date(
                    date(2024, 1, 1),
                    date(2026, 8, 31)
                ),
                "region": random.randint(1, 5),
                "status": random.choice(statuses)
            }
        )

    # -------------------------
    # ORDER ITEMS
    # -------------------------
    conn.execute(text("""
        CREATE TABLE order_items (
            order_item_id INT PRIMARY KEY,
            order_id INT,
            product_id INT,
            quantity INT,
            unit_price DECIMAL(10,2),
            FOREIGN KEY (order_id)
                REFERENCES orders(order_id),
            FOREIGN KEY (product_id)
                REFERENCES products(product_id)
        )
    """))

    item_id = 1

    for order_id in range(1, 10001):
        for _ in range(random.randint(1, 5)):

            product_id = random.randint(1, 500)

            price = conn.execute(
                text("""
                    SELECT price
                    FROM products
                    WHERE product_id = :id
                """),
                {"id": product_id}
            ).scalar()

            conn.execute(
                text("""
                    INSERT INTO order_items
                    VALUES (
                        :item_id,
                        :order_id,
                        :product_id,
                        :quantity,
                        :price
                    )
                """),
                {
                    "item_id": item_id,
                    "order_id": order_id,
                    "product_id": product_id,
                    "quantity": random.randint(1, 10),
                    "price": price
                }
            )

            item_id += 1


print("Database populated successfully!")
print("Customers: 5,000")
print("Products: 500")
print("Employees: 1,000")
print("Orders: 10,000")
print("Order items: 30,000+")