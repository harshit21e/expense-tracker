import os
import sqlite3

from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "expense_tracker.db",
)


def get_db(db_path=None):
    if db_path is None:
        db_path = DB_PATH
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path=None):
    conn = get_db(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            email         TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            amount      REAL NOT NULL,
            category    TEXT NOT NULL,
            description TEXT,
            date        TEXT NOT NULL,
            created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()


def get_user_by_email(email, db_path=None):
    conn = get_db(db_path)
    row = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,),
    ).fetchone()
    conn.close()
    return row


def create_user(name, email, password_hash, db_path=None):
    conn = get_db(db_path)
    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (name, email, password_hash),
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id


def seed_db(db_path=None):
    conn = get_db(db_path)

    existing = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if existing > 0:
        conn.close()
        return

    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@example.com", generate_password_hash("password123")),
    )
    user_id = cursor.lastrowid

    sample_expenses = [
        (user_id, 12.50, "Food", "Lunch at cafe", "2026-07-01"),
        (user_id, 45.00, "Transport", "Monthly bus pass", "2026-07-03"),
        (user_id, 89.99, "Utilities", "Electricity bill", "2026-07-10"),
        (user_id, 25.00, "Food", "Groceries", "2026-07-15"),
        (user_id, 60.00, "Entertainment", "Concert ticket", "2026-07-20"),
    ]
    conn.executemany(
        """
        INSERT INTO expenses (user_id, amount, category, description, date)
        VALUES (?, ?, ?, ?, ?)
        """,
        sample_expenses,
    )

    conn.commit()
    conn.close()
