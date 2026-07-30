# Spec: Registration

## Overview
Spendly currently renders the registration form (`GET /register`) but has no
way to actually create a user. This step implements the `POST /register`
handler so a visitor can submit the existing form, have their input
validated, their password hashed, and a new row inserted into the `users`
table — then be redirected to log in. This is the first step that writes to
the database from a live request (previously only `seed_db()` inserted
users), and it unblocks Step 3 (login) which needs real user rows to
authenticate against.

## Depends on
- Step 1 — Database setup (`database/db.py`, `users` table, `get_db()`)

## Routes
- `POST /register` — validate submitted name/email/password, hash the
  password, insert a new user, redirect to `GET /login` on success or
  re-render `register.html` with an error on failure — public

## Database changes
No database changes. The `users` table (`id`, `name`, `email`,
`password_hash`, `created_at`) already supports registration as-is —
verified against `database/db.py`.

## Templates
- **Create:** none
- **Modify:** `templates/register.html` — form already posts to `/register`;
  update the `action` to use `url_for('register')` instead of the hardcoded
  `/register` string, and confirm the `{% if error %}` block surfaces
  validation/duplicate-email errors returned by the route

## Files to change
- `app.py` — add `POST` handling to the existing `register` view
- `database/db.py` — add a `create_user(name, email, password_hash)` helper
  and a `get_user_by_email(email)` helper (for the duplicate-email check)
- `templates/register.html` — fix hardcoded form action

## Files to create
None.

## New dependencies
No new dependencies. `werkzeug.security.generate_password_hash` is already
used in `database/db.py`.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only (`?` placeholders, no f-strings in SQL)
- Passwords hashed with werkzeug (`generate_password_hash`)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- DB logic stays in `database/db.py` — never inline SQL in `app.py`
- Reject registration if the email already exists (case-insensitive) and
  re-render the form with an error instead of raising an unhandled
  IntegrityError
- Use `abort()` for real HTTP errors — not bare `return "error string"`

## Definition of done
- [ ] Visiting `/register` and submitting a new name/email/password creates
      a row in the `users` table with a hashed password (not plaintext)
- [ ] After successful registration, the browser is redirected to `/login`
- [ ] Submitting a duplicate email re-renders `register.html` with an error
      message and does not create a second row
- [ ] Submitting with a missing field re-renders `register.html` with an
      error instead of a 500 error
- [ ] No plaintext password ever appears in the `users` table or in logs
- [ ] `python app.py` still starts cleanly on port 5001 with no errors
