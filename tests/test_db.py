import sqlite3

import pytest

from database.db import create_user, get_db, get_user_by_email, init_db, seed_db


@pytest.fixture
def db_path(tmp_path):
    path = str(tmp_path / "test.db")
    init_db(path)
    yield path


def test_init_db_creates_tables(db_path):
    conn = get_db(db_path)
    tables = {
        row["name"]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    conn.close()
    assert {"users", "expenses"} <= tables


def test_init_db_users_columns(db_path):
    conn = get_db(db_path)
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(users)").fetchall()}
    conn.close()
    assert columns == {"id", "name", "email", "password_hash", "created_at"}


def test_init_db_expenses_columns(db_path):
    conn = get_db(db_path)
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(expenses)").fetchall()}
    conn.close()
    assert columns == {
        "id",
        "user_id",
        "amount",
        "category",
        "description",
        "date",
        "created_at",
    }


def test_get_db_row_factory_allows_column_access(db_path):
    conn = get_db(db_path)
    conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Alice", "alice@example.com", "hashed"),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM users WHERE email = ?", ("alice@example.com",)).fetchone()
    conn.close()
    assert row["email"] == "alice@example.com"
    assert row["name"] == "Alice"


def test_foreign_keys_enforced(db_path):
    conn = get_db(db_path)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO expenses (user_id, amount, category, date) VALUES (?, ?, ?, ?)",
            (999, 10.0, "Food", "2026-01-01"),
        )
        conn.commit()
    conn.close()


def test_seed_db_inserts_demo_data(db_path):
    seed_db(db_path)
    conn = get_db(db_path)
    user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    expense_count = conn.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]
    conn.close()
    assert user_count == 1
    assert expense_count == 5


def test_users_email_unique_constraint(db_path):
    conn = get_db(db_path)
    conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Alice", "alice@example.com", "hashed"),
    )
    conn.commit()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Bob", "alice@example.com", "hashed"),
        )
        conn.commit()
    conn.close()


def test_seed_db_is_idempotent(db_path):
    seed_db(db_path)
    seed_db(db_path)
    conn = get_db(db_path)
    user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()
    assert user_count == 1


def test_create_user_inserts_row(db_path):
    create_user("Alice", "alice@example.com", "hashed-pw", db_path)
    conn = get_db(db_path)
    row = conn.execute("SELECT * FROM users WHERE email = ?", ("alice@example.com",)).fetchone()
    conn.close()
    assert row["name"] == "Alice"
    assert row["email"] == "alice@example.com"
    assert row["password_hash"] == "hashed-pw"


def test_create_user_returns_id(db_path):
    user_id = create_user("Alice", "alice@example.com", "hashed-pw", db_path)
    conn = get_db(db_path)
    row = conn.execute("SELECT id FROM users WHERE email = ?", ("alice@example.com",)).fetchone()
    conn.close()
    assert user_id == row["id"]


def test_create_user_duplicate_email_raises_integrity_error(db_path):
    create_user("Alice", "alice@example.com", "hashed-pw", db_path)
    with pytest.raises(sqlite3.IntegrityError):
        create_user("Bob", "alice@example.com", "hashed-pw", db_path)


def test_get_user_by_email_returns_row_when_found(db_path):
    create_user("Alice", "alice@example.com", "hashed-pw", db_path)
    row = get_user_by_email("alice@example.com", db_path)
    assert row is not None
    assert row["name"] == "Alice"


def test_get_user_by_email_returns_none_when_not_found(db_path):
    row = get_user_by_email("nobody@example.com", db_path)
    assert row is None


def test_get_user_by_email_is_case_sensitive_at_db_layer(db_path):
    create_user("Alice", "alice@example.com", "hashed-pw", db_path)
    row = get_user_by_email("ALICE@example.com", db_path)
    assert row is None
