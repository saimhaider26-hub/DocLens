import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "company_data.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            location TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            amount REAL,
            status TEXT,
            issue_date TEXT
        )
    """)
    
    cursor.executemany("INSERT OR IGNORE INTO customers VALUES (?, ?, ?, ?)", [
        (1, "Saim Haider", "saim@example.com", "Islamabad"),
        (2, "Abdullah Khan", "abdullah@example.com", "Peshawar"),
        (3, "Sarmad Ahmed", "sarmad@example.com", "Lahore")
    ])
    
    cursor.executemany("INSERT OR IGNORE INTO invoices VALUES (?, ?, ?, ?, ?)", [
        (101, 1, 1500.0, "PAID", "2026-06-01"),
        (102, 1, 800.0, "PENDING", "2026-07-01"),
        (103, 2, 2500.0, "PAID", "2026-05-15"),
        (104, 3, 300.0, "UNPAID", "2026-06-20")
    ])
    
    conn.commit()
    conn.close()
    print(f"Mock database initialized successfully at {DB_PATH}")

if __name__ == "__main__":
    init_db()