import os
from pathlib import Path

# Load .env file if it exists (local dev)
_env_file = Path(__file__).resolve().parent.parent / ".env"
if _env_file.exists():
    for line in _env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            os.environ.setdefault(key.strip(), val.strip())

# If DATABASE_URL is set, use Postgres. Otherwise fall back to SQLite.
DATABASE_URL = os.environ.get("DATABASE_URL")

# SQLite fallback for local dev
_default_db = "/tmp/sharesense.db" if os.environ.get("VERCEL") else "sharesense.db"
DATABASE_PATH = os.environ.get("DATABASE_PATH", _default_db)

JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-change-me")
JWT_EXPIRES_HOURS = int(os.environ.get("JWT_EXPIRES_HOURS", "168"))
PORT = int(os.environ.get("PORT", "3000"))
