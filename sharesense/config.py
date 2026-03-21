import os

# If DATABASE_URL is set, use Postgres. Otherwise fall back to SQLite.
DATABASE_URL = os.environ.get("DATABASE_URL")

# SQLite fallback for local dev
_default_db = "/tmp/sharesense.db" if os.environ.get("VERCEL") else "sharesense.db"
DATABASE_PATH = os.environ.get("DATABASE_PATH", _default_db)

JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-change-me")
JWT_EXPIRES_HOURS = int(os.environ.get("JWT_EXPIRES_HOURS", "168"))
PORT = int(os.environ.get("PORT", "3000"))
