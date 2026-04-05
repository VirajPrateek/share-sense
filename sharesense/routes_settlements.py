import uuid
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify

from auth import login_required, dict_row
from database import get_db
import config

bp = Blueprint("settlements", __name__, url_prefix="/api/groups")


def is_member(db, group_id, user_id):
    return db.execute("SELECT id FROM group_members WHERE group_id = ? AND user_id = ?", (group_id, user_id)).fetchone() is not None


@bp.route("/<group_id>/settlements", methods=["POST"])
@login_required
def create_settlement(group_id):
    """Simplified: "I paid this person this amount". Auto-confirms for the payer."""
    data = request.get_json(silent=True) or {}
    paid_to = data.get("paidTo")
    amount = data.get("amount")

    if not paid_to or not amount:
        return jsonify({"error": "paidTo and amount are required"}), 400
    if float(amount) <= 0:
        return jsonify({"error": "Amount must be greater than 0"}), 400
    if paid_to == request.user_id:
        return jsonify({"error": "Cannot settle with yourself"}), 400

    db = get_db()
    if not is_member(db, group_id, request.user_id):
        db.close()
        return jsonify({"error": "Access denied"}), 403
    if not is_member(db, group_id, paid_to):
        db.close()
        return jsonify({"error": "That person is not in this group"}), 400

    settlement_id = str(uuid.uuid4())
    # Proposer is the debtor (person who paid)
    db.execute(
        "INSERT INTO settlements (id, group_id, debtor_id, creditor_id, amount, status, proposed_by) VALUES (?, ?, ?, ?, ?, 'pending', ?)",
        (settlement_id, group_id, request.user_id, paid_to, round(float(amount), 2), request.user_id),
    )
    # Auto-confirm for the proposer
    db.execute(
        "INSERT INTO settlement_confirmations (id, settlement_id, confirmed_by) VALUES (?, ?, ?)",
        (str(uuid.uuid4()), settlement_id, request.user_id),
    )
    db.commit()
    settlement = dict_row(db.execute(
        """SELECT s.id, s.debtor_id, s.creditor_id, s.amount, s.status, s.created_at,
                  d.name as debtor_name, c.name as creditor_name
           FROM settlements s JOIN users d ON s.debtor_id = d.id JOIN users c ON s.creditor_id = c.id
           WHERE s.id = ?""",
        (settlement_id,),
    ).fetchone())
    db.close()
    return jsonify({"message": "Settlement proposed — waiting for confirmation", "settlement": settlement}), 201


@bp.route("/<group_id>/settlements", methods=["GET"])
@login_required
def get_settlements(group_id):
    db = get_db()
    if not is_member(db, group_id, request.user_id):
        db.close()
        return jsonify({"error": "Access denied"}), 403

    rows = db.execute(
        """SELECT s.id, s.debtor_id, s.creditor_id, s.amount, s.status, s.created_at,
                  d.name as debtor_name, c.name as creditor_name
           FROM settlements s
           JOIN users d ON s.debtor_id = d.id
           JOIN users c ON s.creditor_id = c.id
           WHERE s.group_id = ? AND (s.debtor_id = ? OR s.creditor_id = ?)
           ORDER BY s.created_at DESC""",
        (group_id, request.user_id, request.user_id),
    ).fetchall()

    # Count pending settlements that need current user's confirmation
    pending_for_me = 0
    for r in rows:
        if r["status"] == "pending":
            # Check if current user hasn't confirmed yet and is involved
            if r["debtor_id"] == request.user_id or r["creditor_id"] == request.user_id:
                confirmed = db.execute(
                    "SELECT id FROM settlement_confirmations WHERE settlement_id = ? AND confirmed_by = ?",
                    (r["id"], request.user_id),
                ).fetchone()
                if not confirmed:
                    pending_for_me += 1

    db.close()
    return jsonify({"settlements": [dict(r) for r in rows], "pendingForMe": pending_for_me}), 200


@bp.route("/<group_id>/settlements/<settlement_id>/confirm", methods=["POST"])
@login_required
def confirm_settlement(group_id, settlement_id):
    db = get_db()
    if not is_member(db, group_id, request.user_id):
        db.close()
        return jsonify({"error": "Access denied"}), 403

    settlement = db.execute("SELECT * FROM settlements WHERE id = ? AND group_id = ?", (settlement_id, group_id)).fetchone()
    if not settlement:
        db.close()
        return jsonify({"error": "Settlement not found"}), 404
    if settlement["status"] == "confirmed":
        db.close()
        return jsonify({"error": "Settlement already confirmed"}), 409

    # Record confirmation
    existing = db.execute(
        "SELECT id FROM settlement_confirmations WHERE settlement_id = ? AND confirmed_by = ?",
        (settlement_id, request.user_id),
    ).fetchone()
    if not existing:
        db.execute(
            "INSERT INTO settlement_confirmations (id, settlement_id, confirmed_by) VALUES (?, ?, ?)",
            (str(uuid.uuid4()), settlement_id, request.user_id),
        )

    # Check if both parties confirmed
    debtor_confirmed = db.execute(
        "SELECT id FROM settlement_confirmations WHERE settlement_id = ? AND confirmed_by = ?",
        (settlement_id, settlement["debtor_id"]),
    ).fetchone()
    creditor_confirmed = db.execute(
        "SELECT id FROM settlement_confirmations WHERE settlement_id = ? AND confirmed_by = ?",
        (settlement_id, settlement["creditor_id"]),
    ).fetchone()

    if debtor_confirmed and creditor_confirmed:
        now_val = datetime.now(timezone.utc).isoformat()
        db.execute(
            "UPDATE settlements SET status = 'confirmed', confirmed_at = ? WHERE id = ?",
            (now_val, settlement_id),
        )

    db.commit()
    updated = dict_row(db.execute("SELECT * FROM settlements WHERE id = ?", (settlement_id,)).fetchone())
    db.close()
    return jsonify({"message": "Confirmation recorded", "settlement": updated}), 200
