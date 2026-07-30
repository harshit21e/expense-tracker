# Spec: Login and Logout

## Overview
Spendly can register users and render the login form, but there is no way to
actually authenticate. This step implements `POST /login` so a registered
user can submit their email and password, have their credentials verified
against the hashed password stored in the `users` table, and be signed in
via a server-side session. It also implements `GET /logout` to clear that
session. Together these give Spendly its first notion of "who is currently
logged in," which Step 4 (profile) and all later expense routes depend on.

## Depends on
- Step 1 — Database setup (`database/db.py`, `users` table, `get_db()`)
- Step 2 — Registration (`create_user`, `get_user_by_email`, hashed
  passwords already being written to the `users` table)

## Routes
- `POST /login` — validate submitted email/password against the `users`
  table, verify the password with `check_password_hash`, store the user's
  id in the session, redirect to `GET /profile` on success or re-render
  `login.html` with an error on failure — public
- `GET /logout` — clear the current session and redirect to `GET /` —
  logged-in (safe to call even if no session exists)

## Database changes
No database changes. The `users` table (`id`, `name`, `email`,
`password_hash`, `created_at`) already has everything needed to authenticate
— verified against `database/db.py`. `get_user_by_email` already exists and
will be reused as-is.

## Templates
- **Create:** none
- **Modify:**
  - `templates/login.html` — fix hardcoded `action="/login"` to
    `url_for('login')`; confirm the existing `{% if error %}` block
    surfaces invalid-credential errors returned by the route
  - `templates/base.html` — nav currently always shows "Sign in" /
    "Get started". Make it session-aware: when `session.user_id` is set,
    show a "Sign out" link (`url_for('logout')`) instead of "Sign in" /
    "Get started", so logged-in state can actually be exercised and undone
    through the UI

## Files to change
- `app.py` — set `app.secret_key` (from `os.environ.get("SECRET_KEY", ...)`
  with a dev fallback), add `POST` handling to the existing `login` view,
  implement the `logout` view (remove the Step 3 stub)
- `templates/login.html` — fix hardcoded form action
- `templates/base.html` — session-aware nav links

## Files to create
None.

## New dependencies
No new dependencies. Flask's session support (`flask.session`, backed by
`itsdangerous`) ships with Flask already; `werkzeug.security` already
provides `check_password_hash` alongside the `generate_password_hash` used
in registration.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only (`?` placeholders, no f-strings in SQL) — reuse
  `get_user_by_email`, do not write new inline SQL in `app.py`
- Passwords hashed with werkzeug — verify with `check_password_hash`,
  never compare plaintext
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- DB logic stays in `database/db.py` — never inline SQL in `app.py`
- On failed login, show one generic error ("Invalid email or password")
  for both "no such user" and "wrong password" cases — never reveal
  whether an email is registered
- `logout` must not error if there is no active session — clearing an
  already-empty session is a no-op, not a failure
- Use `abort()` for real HTTP errors — not bare `return "error string"`
- Do not touch the `/profile` or `/expenses/*` stub routes — they belong
  to later steps

## Definition of done
- [ ] Submitting correct credentials on `/login` redirects to `/profile`
- [ ] Submitting a wrong password re-renders `login.html` with a generic
      "Invalid email or password" error and does not create a session
- [ ] Submitting an email that doesn't exist shows the same generic error
      (no difference in wording from a wrong-password failure)
- [ ] After a successful login, visiting `/logout` clears the session and
      redirects to `/`
- [ ] After `/logout`, the nav bar again shows "Sign in" / "Get started"
      instead of "Sign out"
- [ ] Visiting `/logout` without ever logging in does not raise an error
- [ ] `python app.py` still starts cleanly on port 5001 with no errors
