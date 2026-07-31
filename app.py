import os
import sqlite3

from flask import Flask, abort, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database.db import create_user, get_user_by_email, init_db, seed_db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-insecure-secret-key")

CATEGORY_BADGE_CLASSES = {
    "Food": "badge-cat-1",
    "Transport": "badge-cat-2",
    "Utilities": "badge-cat-3",
    "Entertainment": "badge-cat-4",
}


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not name or not email or not password:
        return render_template("register.html", error="All fields are required.")

    if len(password) < 8:
        return render_template(
            "register.html", error="Password must be at least 8 characters."
        )

    if get_user_by_email(email):
        return render_template(
            "register.html", error="An account with that email already exists."
        )

    password_hash = generate_password_hash(password)
    try:
        create_user(name, email, password_hash)
    except sqlite3.IntegrityError:
        return render_template(
            "register.html", error="An account with that email already exists."
        )

    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    user = get_user_by_email(email)

    if not user or not check_password_hash(user["password_hash"], password):
        return render_template("login.html", error="Invalid email or password")

    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    return redirect(url_for("profile"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    user = {
        "name": "Demo User",
        "email": "demo@example.com",
        "initials": "DU",
        "member_since": "March 2026",
    }

    summary_stats = {
        "total_spent": 232.49,
        "transaction_count": 5,
        "top_category": "Utilities",
    }

    transactions = [
        {"date": "2026-07-20", "description": "Concert ticket", "category": "Entertainment", "amount": 60.00},
        {"date": "2026-07-15", "description": "Groceries", "category": "Food", "amount": 25.00},
        {"date": "2026-07-10", "description": "Electricity bill", "category": "Utilities", "amount": 89.99},
        {"date": "2026-07-03", "description": "Monthly bus pass", "category": "Transport", "amount": 45.00},
        {"date": "2026-07-01", "description": "Lunch at cafe", "category": "Food", "amount": 12.50},
    ]

    category_breakdown = [
        {"category": "Utilities", "total": 89.99, "percent": 39},
        {"category": "Entertainment", "total": 60.00, "percent": 26},
        {"category": "Transport", "total": 45.00, "percent": 19},
        {"category": "Food", "total": 37.50, "percent": 16},
    ]

    return render_template(
        "profile.html",
        user=user,
        summary_stats=summary_stats,
        transactions=transactions,
        category_breakdown=category_breakdown,
        category_classes=CATEGORY_BADGE_CLASSES,
    )


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    init_db()
    seed_db()
    app.run(debug=True, port=5001)
