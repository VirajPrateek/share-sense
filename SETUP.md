# ShareSense Setup Guide

## Prerequisites

- Python 3.8+ (run with `py` or `python`)

That's it. No Node.js, no PostgreSQL, no extra services.

## Setup

### 1. Install dependencies

```bash
py -m pip install -r py_backend/requirements.txt
```

This installs Flask, PyJWT, and Flask-CORS.

### 2. Run the app

```bash
py py_backend/app.py
```

The SQLite database (`sharesense.db`) is created automatically on first run.

### 3. Open in browser

Go to http://localhost:3000

Register an account, login, and start creating flats.

## Configuration

Set environment variables to override defaults:

| Variable | Default | Description |
|---|---|---|
| `PORT` | 3000 | Server port |
| `JWT_SECRET` | dev-secret-change-me | JWT signing key |
| `JWT_EXPIRES_HOURS` | 168 (7 days) | Token expiry |
| `DATABASE_PATH` | sharesense.db | SQLite file path |

## Troubleshooting

### Port already in use

Set a different port:
```bash
set PORT=3001
py py_backend/app.py
```

### Module not found errors

Make sure you installed dependencies:
```bash
py -m pip install -r py_backend/requirements.txt
```

### Database issues

Delete `sharesense.db` and restart the app to get a fresh database.
