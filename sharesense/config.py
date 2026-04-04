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

# Supabase Postgres connection
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is required")

JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-change-me")
JWT_EXPIRES_HOURS = int(os.environ.get("JWT_EXPIRES_HOURS", "168"))
PORT = int(os.environ.get("PORT", "3000"))

# Gemini API key for receipt parsing (optional)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
