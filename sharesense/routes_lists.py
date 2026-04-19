import uuid
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify

from auth import login_required, dict_row
from database import get_db

bp = Blueprint("lists", __name__, url_prefix="/api/groups")


def is_member(db, group_id, user_id):
    return db.execute("SELECT id FROM group_members WHERE group_id = ? AND user_id = ?", (group_id, user_id)).fetchone() is not None


@bp.route("/<group_id>/list", methods=["GET"])
@login_required
def get_list(group_id):
    db = get_db()
    if not is_member(db, group_id, request.user_id):
        db.close()
        return jsonify({"error": "Access denied"}), 403

    rows = db.execute(
        """SELECT li.id, li.text, li.is_done, li.created_by, li.created_at, u.name as created_by_name
           FROM list_items li JOIN users u ON li.created_by = u.id
           WHERE li.group_id = ? ORDER BY li.is_done ASC, li.created_at ASC""",
        (group_id,),
    ).fetchall()
    db.close()
    return jsonify({"items": [dict(r) for r in rows]}), 200


@bp.route("/<group_id>/list", methods=["POST"])
@login_required
def add_item(group_id):
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    item_id = data.get("id") or str(uuid.uuid4())  # allow client to provide ID for offline sync

    if not text:
        return jsonify({"error": "Text is required"}), 400

    db = get_db()
    if not is_member(db, group_id, request.user_id):
        db.close()
        return jsonify({"error": "Access denied"}), 403

    db.execute(
        "INSERT INTO list_items (id, group_id, text, created_by) VALUES (?, ?, ?, ?) ON CONFLICT (id) DO NOTHING",
        (item_id, group_id, text, request.user_id),
    )
    db.commit()
    item = dict_row(db.execute(
        "SELECT li.id, li.text, li.is_done, li.created_by, li.created_at, u.name as created_by_name FROM list_items li JOIN users u ON li.created_by = u.id WHERE li.id = ?",
        (item_id,),
    ).fetchone())
    db.close()
    return jsonify({"item": item}), 201


@bp.route("/<group_id>/list/<item_id>", methods=["PATCH"])
@login_required
def toggle_item(group_id, item_id):
    db = get_db()
    if not is_member(db, group_id, request.user_id):
        db.close()
        return jsonify({"error": "Access denied"}), 403

    item = db.execute("SELECT id, is_done FROM list_items WHERE id = ? AND group_id = ?", (item_id, group_id)).fetchone()
    if not item:
        db.close()
        return jsonify({"error": "Item not found"}), 404

    new_state = not item["is_done"]
    db.execute("UPDATE list_items SET is_done = ?, updated_at = ? WHERE id = ?",
               (new_state, datetime.now(timezone.utc).isoformat(), item_id))
    db.commit()
    db.close()
    return jsonify({"id": item_id, "is_done": new_state}), 200


@bp.route("/<group_id>/list/<item_id>", methods=["DELETE"])
@login_required
def delete_item(group_id, item_id):
    db = get_db()
    if not is_member(db, group_id, request.user_id):
        db.close()
        return jsonify({"error": "Access denied"}), 403

    db.execute("DELETE FROM list_items WHERE id = ? AND group_id = ?", (item_id, group_id))
    db.commit()
    db.close()
    return jsonify({"message": "Deleted"}), 200
