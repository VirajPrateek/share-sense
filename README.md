# ShareSense

A lightweight web app for roommates and groups to track shared expenses and settle debts.

## Tech Stack

- Python + Flask (backend & UI)
- SQLite (database, zero setup)
- JWT authentication
- Vanilla HTML/CSS/JS frontend served by Flask

## Quick Start

```bash
# Install dependencies (one time)
py -m pip install -r py_backend/requirements.txt

# Run the app
py py_backend/app.py
```

Open http://localhost:3000 in your browser.

## Features

- User registration & login (JWT auth)
- Create and manage flats/groups
- Add/remove members
- Expense tracking (in progress)
- Settlement management (in progress)

## API Endpoints

### Auth
- `POST /api/auth/register` — Register a new user
- `POST /api/auth/login` — Login, returns JWT token
- `GET /api/auth/me` — Get current user profile
- `POST /api/auth/logout` — Logout

### Flats
- `POST /api/flats` — Create a flat
- `GET /api/flats` — List your flats
- `GET /api/flats/:id` — Get flat details
- `GET /api/flats/:id/members` — List flat members
- `POST /api/flats/:id/members` — Add a member
- `DELETE /api/flats/:id/members/:userId` — Remove a member

## Project Structure

```
py_backend/
├── app.py              # Flask app + entry point
├── auth.py             # JWT + password hashing
├── config.py           # Configuration (env vars)
├── database.py         # SQLite schema + connection
├── requirements.txt    # Python dependencies
├── routes_auth.py      # Auth API routes
├── routes_flats.py     # Flats API routes
└── templates/
    └── base.html       # Single-page UI
```
