import os

DATABASE_PATH = os.environ.get("DATABASE_PATH", "sharesense.db")
JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-change-me")
JWT_EXPIRES_HOURS = int(os.environ.get("JWT_EXPIRES_HOURS", "168"))  # 7 days
PORT = int(os.environ.get("PORT", "3000"))
