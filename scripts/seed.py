"""Deterministically build the synthetic database. Never touch user databases."""
from datetime import date, timedelta
from pathlib import Path
import random
import sqlite3

ROOT = Path(__file__).resolve().parents[1]


def build() -> None:
    target = ROOT / "data" / "sample.db"
    temporary = target.with_suffix(".building.db")
    if temporary.exists():
        temporary.unlink()
    rng = random.Random(20241105)
    first = ["Avery", "Jordan", "Morgan", "Riley", "Taylor", "Casey", "Quinn", "Alex", "Sam", "Jamie", "Reese", "Cameron"]
    last = ["Chen", "Patel", "Williams", "Garcia", "Kim", "Davis", "Wilson", "Singh", "Brown", "Lopez"]
    locations = [("San Francisco", "California"), ("Los Angeles", "California"), ("Austin", "Texas"), ("Seattle", "Washington"), ("New York", "New York"), ("Denver", "Colorado"), ("Portland", "Oregon"), ("Chicago", "Illinois")]
    with sqlite3.connect(temporary) as db:
        db.executescript((ROOT / "data" / "schema.sql").read_text())
        db.executemany("INSERT INTO departments VALUES (?, ?)", enumerate(["Sales", "Engineering", "Operations", "Customer Success"], 1))
        for i in range(1, 25):
            name = f"{first[(i-1)%12]} {last[(i-1)//3%10]}"
            hired = date(2023, 1, 1) + timedelta(days=i * 32)
            db.execute("INSERT INTO employees VALUES (?,?,?,?,?,?)", (i, name, f"employee{i}@northstar.example", (i-1)%4+1, hired.isoformat(), 58000+i*2700))
        for i in range(1, 121):
            city, state = locations[(i-1)%len(locations)]
            name = f"{first[(i-1)%12]} {last[(i-1)//12]}"
            db.execute("INSERT INTO customers VALUES (?,?,?,?,?,?)", (i, name, f"customer{i}@example.com", city, state, (date(2023, 1, 1)+timedelta(days=i*5)).isoformat()))
        products = [("Studio Headphones", "Electronics", 149), ("Mechanical Keyboard", "Electronics", 129), ("4K Monitor", "Electronics", 399), ("Desk Lamp", "Home Office", 69), ("Standing Desk", "Home Office", 549), ("Ergonomic Chair", "Home Office", 329), ("Canvas Backpack", "Accessories", 89), ("Laptop Sleeve", "Accessories", 39), ("Travel Mug", "Lifestyle", 29), ("Notebook Set", "Lifestyle", 19), ("Wireless Mouse", "Electronics", 59), ("USB-C Hub", "Electronics", 79), ("Desk Mat", "Home Office", 35), ("Webcam", "Electronics", 99), ("Water Bottle", "Lifestyle", 25), ("Cable Organizer", "Accessories", 15), ("Portable Speaker", "Electronics", 119), ("Reading Light", "Home Office", 45)]
        db.executemany("INSERT INTO products VALUES (?,?,?,?)", [(i, *p) for i, p in enumerate(products, 1)])
        item_id = 0
        for i in range(1, 361):
            ordered = date(2024, 1, 1) + timedelta(days=(i*2)%730)
            status = "cancelled" if i%13 == 0 else "processing" if i%11 == 0 else "completed"
            db.execute("INSERT INTO orders VALUES (?,?,?,?,?)", (i, rng.randint(1,120), rng.randint(1,24), ordered.isoformat(), status))
            for _ in range(2+i%2):
                item_id += 1
                product_id = rng.randint(1,18)
                unit_price = round(products[product_id-1][2] * rng.choice([1,1,1,0.9]), 2)
                db.execute("INSERT INTO order_items VALUES (?,?,?,?,?)", (item_id, i, product_id, rng.randint(1,4), unit_price))
        db.execute("ANALYZE")
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []
        assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    db.close()  # sqlite's transaction context manager does not close the handle on Windows.
    temporary.replace(target)
    print(f"Built {target.name}: 6 tables, 120 customers, 24 employees, 360 orders, {item_id} items")


if __name__ == "__main__":
    build()
