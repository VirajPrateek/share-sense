import uuid
import random
import string

from flask import Blueprint, request, jsonify

from auth import login_required, dict_row
from database import get_db

bp = Blueprint("groups", __name__, url_prefix="/api/groups")


def _gen_join_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


def is_member(db, group_id, user_id):
    return db.execute("SELECT id FROM group_members WHERE group_id = ? AND user_id = ?", (group_id, user_id)).fetchone() is not None


def is_admin(db, group_id, user_id):
    row = db.execute("SELECT created_by FROM groups WHERE id = ?", (group_id,)).fetchone()
    return row and row["created_by"] == user_id


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
    join_code = _gen_join_code()

    db = get_db()
    # Ensure unique join code
    for _ in range(5):
        if not db.execute("SELECT id FROM groups WHERE join_code = ?", (join_code,)).fetchone():
            break
        join_code = _gen_join_code()

    db.execute("INSERT INTO groups (id, name, created_by, join_code) VALUES (?, ?, ?, ?)", (group_id, name, user_id, join_code))
    db.execute("INSERT INTO group_members (id, group_id, user_id) VALUES (?, ?, ?)", (member_id, group_id, user_id))
    db.commit()
    group = dict_row(db.execute("SELECT id, name, created_by, join_code, status, created_at, updated_at FROM groups WHERE id = ?", (group_id,)).fetchone())
    db.close()
    return jsonify({"message": "Group created successfully", "group": group}), 201


@bp.route("", methods=["GET"])
@login_required
def get_user_groups():
    db = get_db()
    rows = db.execute(
        """SELECT g.id, g.name, g.created_by, g.join_code, g.status, g.created_at, g.updated_at, gm.joined_at
           FROM groups g INNER JOIN group_members gm ON g.id = gm.group_id
           WHERE gm.user_id = ? AND g.status = 'active' ORDER BY g.created_at DESC""",
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
    group = dict_row(db.execute("SELECT id, name, created_by, join_code, status, created_at, updated_at FROM groups WHERE id = ?", (group_id,)).fetchone())
    db.close()
    if not group:
        return jsonify({"error": "Group not found"}), 404
    return jsonify({"group": group}), 200


@bp.route("/<group_id>", methods=["DELETE"])
@login_required
def delete_group(group_id):
    db = get_db()
    if not is_admin(db, group_id, request.user_id):
        db.close()
        return jsonify({"error": "Only the group admin can delete this group"}), 403
    db.execute("DELETE FROM groups WHERE id = ?", (group_id,))
    db.commit()
    db.close()
    return jsonify({"message": "Group deleted"}), 200


@bp.route("/<group_id>/archive", methods=["POST"])
@login_required
def archive_group(group_id):
    db = get_db()
    if not is_admin(db, group_id, request.user_id):
        db.close()
        return jsonify({"error": "Only the group admin can archive this group"}), 403
    db.execute("UPDATE groups SET status = 'archived' WHERE id = ?", (group_id,))
    db.commit()
    db.close()
    return jsonify({"message": "Group archived"}), 200


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

    db = get_db()
    # Only admin can add members directly
    if not is_admin(db, group_id, request.user_id):
        db.close()
        return jsonify({"error": "Only the group admin can add members"}), 403

    if not email:
        db.close()
        return jsonify({"error": "Email is required"}), 400

    user_row = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if not user_row:
        db.close()
        return jsonify({"error": "No user found with that email"}), 404

    user_id_to_add = user_row["id"]
    if is_member(db, group_id, user_id_to_add):
        db.close()
        return jsonify({"error": "User is already a member of this group"}), 409

    member_id = str(uuid.uuid4())
    db.execute("INSERT INTO group_members (id, group_id, user_id) VALUES (?, ?, ?)", (member_id, group_id, user_id_to_add))
    db.commit()
    db.close()
    return jsonify({"message": "Member added successfully"}), 201


@bp.route("/join", methods=["POST"])
@login_required
def join_group():
    """Join a group using a 6-char invite code."""
    data = request.get_json(silent=True) or {}
    code = (data.get("code") or "").strip().upper()
    if not code or len(code) != 6:
        return jsonify({"error": "Invalid join code"}), 400

    db = get_db()
    group = db.execute("SELECT id, status FROM groups WHERE join_code = ?", (code,)).fetchone()
    if not group:
        db.close()
        return jsonify({"error": "No group found with that code"}), 404
    if group["status"] != "active":
        db.close()
        return jsonify({"error": "This group is archived"}), 400

    if is_member(db, group["id"], request.user_id):
        db.close()
        return jsonify({"error": "You are already a member of this group"}), 409

    member_id = str(uuid.uuid4())
    db.execute("INSERT INTO group_members (id, group_id, user_id) VALUES (?, ?, ?)", (member_id, group["id"], request.user_id))
    db.commit()
    db.close()
    return jsonify({"message": "Joined group successfully", "groupId": group["id"]}), 201


@bp.route("/<group_id>/members/<user_id>", methods=["DELETE"])
@login_required
def remove_member(group_id, user_id):
    db = get_db()
    # Only admin can remove others; anyone can leave (remove themselves)
    if user_id != request.user_id and not is_admin(db, group_id, request.user_id):
        db.close()
        return jsonify({"error": "Only the group admin can remove members"}), 403
    if not is_member(db, group_id, user_id):
        db.close()
        return jsonify({"error": "User is not a member of this group"}), 404
    # Admin can't remove themselves (would orphan the group)
    if is_admin(db, group_id, user_id):
        db.close()
        return jsonify({"error": "Admin cannot leave the group. Archive or delete it instead."}), 400
    db.execute("DELETE FROM group_members WHERE group_id = ? AND user_id = ?", (group_id, user_id))
    db.commit()
    db.close()
    return jsonify({"message": "Member removed successfully"}), 200
