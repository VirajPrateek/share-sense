import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import request, jsonify

import config
from database import get_db


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return hashed.hex(), salt


def verify_password(password, password_hash, salt):
    hashed, _ = hash_password(password, salt)
    return hashed == password_hash


def create_token(user_id, email):
    payload = {
        "userId": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=config.JWT_EXPIRES_HOURS),
    }
    return jwt.encode(payload, config.JWT_SECRET, algorithm="HS256")


def decode_token(token):
    return jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authentication required", "message": "No token provided"}), 401
        token = auth_header[7:]
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Authentication failed", "message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Authentication failed", "message": "Invalid token"}), 401

        db = get_db()
        user = db.execute("SELECT id, email, name, created_at, updated_at FROM users WHERE id = ?", (payload["userId"],)).fetchone()
        db.close()
        if not user:
            return jsonify({"error": "Authentication failed", "message": "User not found"}), 401

        request.user = dict(user)
        request.user_id = user["id"]
        return f(*args, **kwargs)
    return decorated


def dict_row(row):
    return dict(row) if row else None
