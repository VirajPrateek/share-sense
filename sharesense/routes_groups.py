import uuid

from flask import Blueprint, request, jsonify

from auth import login_required, dict_row
from database import get_db

bp = Blueprint("groups", __name__, url_prefix="/api/groups")


def is_member(db, group_id, user_id):
    return db.execute("SELECT id FROM group_members WHERE group_id = ? AND user_id = ?", (group_id, user_id)).fetchone() is not None


@bp.route("", methods=["POST"])
@login_required
def create_group():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Validation error", "message": "Group name is required"}), 400

    user_id = request.user_id
    group_id = str(uuid.uuid4())
    member_id = str(uuid.uuid4())

    db = get_db()
    db.execute("INSERT INTO groups (id, name, created_by) VALUES (?, ?, ?)", (group_id, name, user_id))
    db.execute("INSERT INTO group_members (id, group_id, user_id) VALUES (?, ?, ?)", (member_id, group_id, user_id))
    db.commit()
    group = dict_row(db.execute("SELECT id, name, created_by, created_at, updated_at FROM groups WHERE id = ?", (group_id,)).fetchone())
    db.close()
    return jsonify({"message": "Group created successfully", "group": group}), 201


@bp.route("", methods=["GET"])
@login_required
def get_user_groups():
    db = get_db()
    rows = db.execute(
        """SELECT g.id, g.name, g.created_by, g.created_at, g.updated_at, gm.joined_at
           FROM groups g INNER JOIN group_members gm ON g.id = gm.group_id
           WHERE gm.user_id = ? ORDER BY g.created_at DESC""",
        (request.user_id,),
    ).fetchall()
    db.close()
    return jsonify({"groups": [dict(r) for r in rows]}), 200


@bp.route("/<group_id>", methods=["GET"])
@login_required
def get_group(group_id):
    db = get_db()
    if not is_member(db, group_id, request.user_id):
        db.close()
        return jsonify({"error": "Access denied", "message": "You are not a member of this group"}), 403
    group = dict_row(db.execute("SELECT id, name, created_by, created_at, updated_at FROM groups WHERE id = ?", (group_id,)).fetchone())
    db.close()
    if not group:
        return jsonify({"error": "Group not found"}), 404
    return jsonify({"group": group}), 200


@bp.route("/<group_id>/members", methods=["GET"])
@login_required
def get_group_members(group_id):
    db = get_db()
    if not is_member(db, group_id, request.user_id):
        db.close()
        return jsonify({"error": "Access denied", "message": "You are not a member of this group"}), 403
    rows = db.execute(
        """SELECT u.id, u.email, u.name, gm.joined_at
           FROM users u INNER JOIN group_members gm ON u.id = gm.user_id
           WHERE gm.group_id = ? ORDER BY gm.joined_at ASC""",
        (group_id,),
    ).fetchall()
    db.close()
    return jsonify({"members": [dict(r) for r in rows]}), 200


@bp.route("/<group_id>/members", methods=["POST"])
@login_required
def add_member(group_id):
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    user_id_to_add = data.get("userId")

    if not email and not user_id_to_add:
        return jsonify({"error": "Validation error", "message": "Email or User ID is required"}), 400

    db = get_db()
    if not is_member(db, group_id, request.user_id):
        db.close()
        return jsonify({"error": "Access denied", "message": "You are not a member of this group"}), 403

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

    if is_member(db, group_id, user_id_to_add):
        db.close()
        return jsonify({"error": "User is already a member of this group"}), 409

    member_id = str(uuid.uuid4())
    db.execute("INSERT INTO group_members (id, group_id, user_id) VALUES (?, ?, ?)", (member_id, group_id, user_id_to_add))
    db.commit()
    member = dict_row(db.execute("SELECT id, group_id, user_id, joined_at FROM group_members WHERE id = ?", (member_id,)).fetchone())
    db.close()
    return jsonify({"message": "Member added successfully", "member": member}), 201


@bp.route("/<group_id>/members/<user_id>", methods=["DELETE"])
@login_required
def remove_member(group_id, user_id):
    db = get_db()
    if not is_member(db, group_id, request.user_id):
        db.close()
        return jsonify({"error": "Access denied", "message": "You are not a member of this group"}), 403
    if not is_member(db, group_id, user_id):
        db.close()
        return jsonify({"error": "User is not a member of this group"}), 404
    db.execute("DELETE FROM group_members WHERE group_id = ? AND user_id = ?", (group_id, user_id))
    db.commit()
    db.close()
    return jsonify({"message": "Member removed successfully"}), 200
