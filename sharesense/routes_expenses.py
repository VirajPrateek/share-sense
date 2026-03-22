import uuid
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify

from auth import login_required, dict_row
from database import get_db

bp = Blueprint("expenses", __name__, url_prefix="/api/flats")


def is_member(db, flat_id, user_id):
    return db.execute("SELECT id FROM flat_members WHERE flat_id = ? AND user_id = ?", (flat_id, user_id)).fetchone() is not None


@bp.route("/<flat_id>/expenses", methods=["POST"])
@login_required
def add_expense(flat_id):
    data = request.get_json(silent=True) or {}
    amount = data.get("amount")
    description = (data.get("description") or "").strip()
    payer_id = data.get("payerId") or request.user_id
    expense_type = data.get("expenseType", "shared")
    timestamp = data.get("timestamp") or datetime.now(timezone.utc).isoformat()

    if not amount or float(amount) <= 0:
        return jsonify({"error": "Amount must be greater than 0"}), 400
    if not description:
        return jsonify({"error": "Description is required"}), 400
    if expense_type not in ("shared", "personal"):
        return jsonify({"error": "Expense type must be 'shared' or 'personal'"}), 400

    amount = round(float(amount), 2)
    db = get_db()

    if not is_member(db, flat_id, request.user_id):
        db.close()
        return jsonify({"error": "Access denied"}), 403

    # Create expense
    expense_id = str(uuid.uuid4())
    db.execute(
        "INSERT INTO expenses (id, amount, description, payer_id, flat_id, expense_type, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (expense_id, amount, description, payer_id, flat_id, expense_type, timestamp),
    )

    # If shared, split equally among all members
    if expense_type == "shared":
        members = db.execute("SELECT user_id FROM flat_members WHERE flat_id = ?", (flat_id,)).fetchall()
        share = round(amount / len(members), 2)
        for m in members:
            db.execute(
                "INSERT INTO expense_shares (id, expense_id, sharer_id, share_amount) VALUES (?, ?, ?, ?)",
                (str(uuid.uuid4()), expense_id, m["user_id"], share),
            )

    db.commit()
    expense = dict_row(db.execute(
        "SELECT id, amount, description, payer_id, flat_id, expense_type, timestamp, created_at FROM expenses WHERE id = ?",
        (expense_id,),
    ).fetchone())
    db.close()
    return jsonify({"message": "Expense added", "expense": expense}), 201


@bp.route("/<flat_id>/expenses", methods=["GET"])
@login_required
def get_expenses(flat_id):
    db = get_db()
    if not is_member(db, flat_id, request.user_id):
        db.close()
        return jsonify({"error": "Access denied"}), 403

    rows = db.execute(
        """SELECT e.id, e.amount, e.description, e.payer_id, e.expense_type, e.timestamp, e.created_at,
                  u.name as payer_name
           FROM expenses e JOIN users u ON e.payer_id = u.id
           WHERE e.flat_id = ? ORDER BY e.timestamp DESC""",
        (flat_id,),
    ).fetchall()
    db.close()
    return jsonify({"expenses": [dict(r) for r in rows]}), 200


@bp.route("/<flat_id>/expenses/<expense_id>", methods=["DELETE"])
@login_required
def delete_expense(flat_id, expense_id):
    db = get_db()
    if not is_member(db, flat_id, request.user_id):
        db.close()
        return jsonify({"error": "Access denied"}), 403

    expense = db.execute("SELECT id FROM expenses WHERE id = ? AND flat_id = ?", (expense_id, flat_id)).fetchone()
    if not expense:
        db.close()
        return jsonify({"error": "Expense not found"}), 404

    db.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    db.commit()
    db.close()
    return jsonify({"message": "Expense deleted"}), 200



@bp.route("/<flat_id>/balances", methods=["GET"])
@login_required
def get_balances(flat_id):
    db = get_db()
    if not is_member(db, flat_id, request.user_id):
        db.close()
        return jsonify({"error": "Access denied"}), 403

    members = db.execute(
        "SELECT u.id, u.name FROM users u JOIN flat_members fm ON u.id = fm.user_id WHERE fm.flat_id = ?",
        (flat_id,),
    ).fetchall()

    # Calculate net balance per person: paid - owed
    balances = {}
    names = {}
    for m in members:
        balances[m["id"]] = 0.0
        names[m["id"]] = m["name"]

    paid = db.execute(
        "SELECT payer_id, SUM(amount) as total FROM expenses WHERE flat_id = ? AND expense_type = 'shared' GROUP BY payer_id",
        (flat_id,),
    ).fetchall()
    for p in paid:
        if p["payer_id"] in balances:
            balances[p["payer_id"]] += float(p["total"])

    owed = db.execute(
        """SELECT es.sharer_id, SUM(es.share_amount) as total
           FROM expense_shares es JOIN expenses e ON es.expense_id = e.id
           WHERE e.flat_id = ? AND e.expense_type = 'shared'
           GROUP BY es.sharer_id""",
        (flat_id,),
    ).fetchall()
    for o in owed:
        if o["sharer_id"] in balances:
            balances[o["sharer_id"]] -= float(o["total"])

    # Factor in confirmed settlements
    settlements = db.execute(
        "SELECT debtor_id, creditor_id, amount FROM settlements WHERE flat_id = ? AND status = 'confirmed'",
        (flat_id,),
    ).fetchall()
    for s in settlements:
        if s["debtor_id"] in balances:
            balances[s["debtor_id"]] += float(s["amount"])
        if s["creditor_id"] in balances:
            balances[s["creditor_id"]] -= float(s["amount"])

    # Simplify debts: greedy algorithm to minimize transactions
    debtors = []  # people who owe (negative balance)
    creditors = []  # people who are owed (positive balance)
    for uid, bal in balances.items():
        bal = round(bal, 2)
        if bal < 0:
            debtors.append({"id": uid, "name": names[uid], "amount": -bal})
        elif bal > 0:
            creditors.append({"id": uid, "name": names[uid], "amount": bal})

    # Match debtors to creditors
    transfers = []
    debtors.sort(key=lambda x: -x["amount"])
    creditors.sort(key=lambda x: -x["amount"])
    di, ci = 0, 0
    while di < len(debtors) and ci < len(creditors):
        d = debtors[di]
        c = creditors[ci]
        amt = round(min(d["amount"], c["amount"]), 2)
        if amt > 0:
            transfers.append({
                "from_id": d["id"], "from_name": d["name"],
                "to_id": c["id"], "to_name": c["name"],
                "amount": amt
            })
        d["amount"] = round(d["amount"] - amt, 2)
        c["amount"] = round(c["amount"] - amt, 2)
        if d["amount"] == 0:
            di += 1
        if c["amount"] == 0:
            ci += 1

    db.close()
    return jsonify({"transfers": transfers}), 200


