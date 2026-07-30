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


def test_get_login_renders_form(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Welcome back" in response.data


def test_post_login_success_redirects_to_profile(client, db_path):
    client.post(
        "/register",
        data={"name": "Alice", "email": "alice@example.com", "password": "password123"},
    )
    response = client.post(
        "/login",
        data={"email": "alice@example.com", "password": "password123"},
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "/profile"

    with client.session_transaction() as sess:
        assert sess["user_id"] is not None


def test_post_login_wrong_password_shows_generic_error(client, db_path):
    client.post(
        "/register",
        data={"name": "Alice", "email": "alice@example.com", "password": "password123"},
    )
    response = client.post(
        "/login",
        data={"email": "alice@example.com", "password": "wrongpass"},
    )
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data

    with client.session_transaction() as sess:
        assert "user_id" not in sess


def test_post_login_unknown_email_shows_same_generic_error(client, db_path):
    response = client.post(
        "/login",
        data={"email": "nobody@example.com", "password": "whatever1"},
    )
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data

    with client.session_transaction() as sess:
        assert "user_id" not in sess


def test_logout_clears_session_and_redirects_home(client, db_path):
    client.post(
        "/register",
        data={"name": "Alice", "email": "alice@example.com", "password": "password123"},
    )
    client.post(
        "/login",
        data={"email": "alice@example.com", "password": "password123"},
    )

    response = client.get("/logout")
    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    with client.session_transaction() as sess:
        assert "user_id" not in sess


def test_logout_without_session_is_noop(client):
    response = client.get("/logout")
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_nav_shows_sign_out_when_logged_in(client, db_path):
    client.post(
        "/register",
        data={"name": "Alice", "email": "alice@example.com", "password": "password123"},
    )
    client.post(
        "/login",
        data={"email": "alice@example.com", "password": "password123"},
    )

    response = client.get("/")
    assert b"Sign out" in response.data
    assert b"Get started" not in response.data


def test_nav_shows_get_started_when_logged_out(client):
    response = client.get("/")
    assert b"Get started" in response.data
    assert b"Sign out" not in response.data
