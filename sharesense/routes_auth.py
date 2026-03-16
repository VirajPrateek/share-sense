import re
import uuid

from flask import Blueprint, request, jsonify

from auth import hash_password, verify_password, create_token, login_required, dict_row
from database import get_db

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")
    name = data.get("name", "").strip()

    if not email or not password or not name:
        return jsonify({"error": "Validation error", "message": "Email, password, and name are required"}), 400
    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        return jsonify({"error": "Validation error", "message": "Invalid email format"}), 400
    if len(password) < 6:
        return jsonify({"error": "Validation error", "message": "Password must be at least 6 characters long"}), 400

    db = get_db()
    if db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone():
        db.close()
        return jsonify({"error": "Email already registered"}), 409

    user_id = str(uuid.uuid4())
    pw_hash, salt = hash_password(password)
    db.execute(
        "INSERT INTO users (id, email, password_hash, salt, name) VALUES (?, ?, ?, ?, ?)",
        (user_id, email, pw_hash, salt, name),
    )
    db.commit()
    user = dict_row(db.execute("SELECT id, email, name, created_at, updated_at FROM users WHERE id = ?", (user_id,)).fetchone())
    db.close()
    return jsonify({"message": "User registered successfully", "user": user}), 201


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "")
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Validation error", "message": "Email and password are required"}), 400

    db = get_db()
    row = db.execute("SELECT id, email, password_hash, salt, name FROM users WHERE email = ?", (email,)).fetchone()
    db.close()

    if not row or not verify_password(password, row["password_hash"], row["salt"]):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_token(row["id"], row["email"])
    user = {"id": row["id"], "email": row["email"], "name": row["name"]}
    return jsonify({"message": "Login successful", "user": user, "token": token}), 200


@bp.route("/me", methods=["GET"])
@login_required
def me():
    return jsonify({"user": request.user}), 200


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    return jsonify({"message": "Logout successful"}), 200
