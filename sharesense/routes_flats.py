import uuid

from flask import Blueprint, request, jsonify

from auth import login_required, dict_row
from database import get_db

bp = Blueprint("flats", __name__, url_prefix="/api/flats")


def is_member(db, flat_id, user_id):
    return db.execute("SELECT id FROM flat_members WHERE flat_id = ? AND user_id = ?", (flat_id, user_id)).fetchone() is not None


@bp.route("", methods=["POST"])
@login_required
def create_flat():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Validation error", "message": "Flat name is required"}), 400

    user_id = request.user_id
    flat_id = str(uuid.uuid4())
    member_id = str(uuid.uuid4())

    db = get_db()
    db.execute("INSERT INTO flats (id, name, created_by) VALUES (?, ?, ?)", (flat_id, name, user_id))
    db.execute("INSERT INTO flat_members (id, flat_id, user_id) VALUES (?, ?, ?)", (member_id, flat_id, user_id))
    db.commit()
    flat = dict_row(db.execute("SELECT id, name, created_by, created_at, updated_at FROM flats WHERE id = ?", (flat_id,)).fetchone())
    db.close()
    return jsonify({"message": "Flat created successfully", "flat": flat}), 201


@bp.route("", methods=["GET"])
@login_required
def get_user_flats():
    db = get_db()
    rows = db.execute(
        """SELECT f.id, f.name, f.created_by, f.created_at, f.updated_at, fm.joined_at
           FROM flats f INNER JOIN flat_members fm ON f.id = fm.flat_id
           WHERE fm.user_id = ? ORDER BY f.created_at DESC""",
        (request.user_id,),
    ).fetchall()
    db.close()
    return jsonify({"flats": [dict(r) for r in rows]}), 200


@bp.route("/<flat_id>", methods=["GET"])
@login_required
def get_flat(flat_id):
    db = get_db()
    if not is_member(db, flat_id, request.user_id):
        db.close()
        return jsonify({"error": "Access denied", "message": "You are not a member of this flat"}), 403
    flat = dict_row(db.execute("SELECT id, name, created_by, created_at, updated_at FROM flats WHERE id = ?", (flat_id,)).fetchone())
    db.close()
    if not flat:
        return jsonify({"error": "Flat not found"}), 404
    return jsonify({"flat": flat}), 200


@bp.route("/<flat_id>/members", methods=["GET"])
@login_required
def get_flat_members(flat_id):
    db = get_db()
    if not is_member(db, flat_id, request.user_id):
        db.close()
        return jsonify({"error": "Access denied", "message": "You are not a member of this flat"}), 403
    rows = db.execute(
        """SELECT u.id, u.email, u.name, fm.joined_at
           FROM users u INNER JOIN flat_members fm ON u.id = fm.user_id
           WHERE fm.flat_id = ? ORDER BY fm.joined_at ASC""",
        (flat_id,),
    ).fetchall()
    db.close()
    return jsonify({"members": [dict(r) for r in rows]}), 200


@bp.route("/<flat_id>/members", methods=["POST"])
@login_required
def add_member(flat_id):
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    user_id_to_add = data.get("userId")

    if not email and not user_id_to_add:
        return jsonify({"error": "Validation error", "message": "Email or User ID is required"}), 400

    db = get_db()
    if not is_member(db, flat_id, request.user_id):
        db.close()
        return jsonify({"error": "Access denied", "message": "You are not a member of this flat"}), 403

    # Look up user by email if no userId provided
    if email and not user_id_to_add:
        user_row = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if not user_row:
            db.close()
            return jsonify({"error": "No user found with that email"}), 404
        user_id_to_add = user_row["id"]
    else:
        if not db.execute("SELECT id FROM users WHERE id = ?", (user_id_to_add,)).fetchone():
            db.close()
            return jsonify({"error": "User not found"}), 404

    if is_member(db, flat_id, user_id_to_add):
        db.close()
        return jsonify({"error": "User is already a member of this flat"}), 409

    member_id = str(uuid.uuid4())
    db.execute("INSERT INTO flat_members (id, flat_id, user_id) VALUES (?, ?, ?)", (member_id, flat_id, user_id_to_add))
    db.commit()
    member = dict_row(db.execute("SELECT id, flat_id, user_id, joined_at FROM flat_members WHERE id = ?", (member_id,)).fetchone())
    db.close()
    return jsonify({"message": "Member added successfully", "member": member}), 201


@bp.route("/<flat_id>/members/<user_id>", methods=["DELETE"])
@login_required
def remove_member(flat_id, user_id):
    db = get_db()
    if not is_member(db, flat_id, request.user_id):
        db.close()
        return jsonify({"error": "Access denied", "message": "You are not a member of this flat"}), 403
    if not is_member(db, flat_id, user_id):
        db.close()
        return jsonify({"error": "User is not a member of this flat"}), 404
    db.execute("DELETE FROM flat_members WHERE flat_id = ? AND user_id = ?", (flat_id, user_id))
    db.commit()
    db.close()
    return jsonify({"message": "Member removed successfully"}), 200
