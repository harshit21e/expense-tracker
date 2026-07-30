from database.db import get_db


def test_get_register_renders_form(client):
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Create your account" in response.data


def test_post_register_success_redirects_to_login(client, db_path):
    response = client.post(
        "/register",
        data={"name": "Alice", "email": "alice@example.com", "password": "password123"},
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "/login"

    conn = get_db(db_path)
    row = conn.execute("SELECT * FROM users WHERE email = ?", ("alice@example.com",)).fetchone()
    conn.close()
    assert row is not None
    assert row["name"] == "Alice"
    assert row["password_hash"] != "password123"


def test_post_register_missing_field_rerenders_with_error(client):
    response = client.post(
        "/register",
        data={"name": "Alice", "email": "alice@example.com", "password": ""},
    )
    assert response.status_code == 200
    assert b"All fields are required." in response.data


def test_post_register_short_password_rerenders_with_error(client):
    response = client.post(
        "/register",
        data={"name": "Alice", "email": "alice@example.com", "password": "short"},
    )
    assert response.status_code == 200
    assert b"Password must be at least 8 characters." in response.data


def test_post_register_duplicate_email_rerenders_with_error(client):
    client.post(
        "/register",
        data={"name": "Alice", "email": "alice@example.com", "password": "password123"},
    )
    response = client.post(
        "/register",
        data={"name": "Bob", "email": "ALICE@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    assert b"An account with that email already exists." in response.data
