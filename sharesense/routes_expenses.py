import uuid
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify

from auth import login_required, dict_row
from database import get_db

bp = Blueprint("expenses", __name__, url_prefix="/api/groups")


def is_member(db, group_id, user_id):
    return db.execute("SELECT id FROM group_members WHERE group_id = ? AND user_id = ?", (group_id, user_id)).fetchone() is not None


@bp.route("/<group_id>/expenses", methods=["POST"])
@login_required
def add_expense(group_id):
    data = request.get_json(silent=True) or {}
    amount = data.get("amount")
    description = (data.get("description") or "").strip()
    expense_type = data.get("expenseType", "shared")
    category = data.get("category", "other")
    sharer_ids = data.get("sharerIds")  # optional list of user IDs to split among
    timestamp = data.get("timestamp") or datetime.now(timezone.utc).isoformat()

    if not amount or float(amount) <= 0:
        return jsonify({"error": "Amount must be greater than 0"}), 400
    if not description:
        return jsonify({"error": "Description is required"}), 400
    if expense_type not in ("shared", "personal"):
        return jsonify({"error": "Expense type must be 'shared' or 'personal'"}), 400

    amount = round(float(amount), 2)
    db = get_db()

    if not is_member(db, group_id, request.user_id):
        db.close()
        return jsonify({"error": "Access denied"}), 403

    # Payer is always the logged-in user — you can only log your own expenses
    payer_id = request.user_id

    # Create expense
    expense_id = str(uuid.uuid4())
    db.execute(
        "INSERT INTO expenses (id, amount, description, payer_id, group_id, expense_type, category, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (expense_id, amount, description, payer_id, group_id, expense_type, category, timestamp),
    )

    # If shared, split among specified members (or all members if not specified)
    if expense_type == "shared":
        if sharer_ids and len(sharer_ids) > 0:
            # Validate all sharer IDs are group members
            members = db.execute("SELECT user_id FROM group_members WHERE group_id = ?", (group_id,)).fetchall()
            member_ids = {m["user_id"] for m in members}
            for sid in sharer_ids:
                if sid not in member_ids:
                    db.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
                    db.commit()
                    db.close()
                    return jsonify({"error": "One or more selected members are not in this group"}), 400
            split_ids = sharer_ids
        else:
            members = db.execute("SELECT user_id FROM group_members WHERE group_id = ?", (group_id,)).fetchall()
            split_ids = [m["user_id"] for m in members]

        if len(split_ids) == 0:
            db.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            db.commit()
            db.close()
            return jsonify({"error": "At least one member must be selected for splitting"}), 400

        share = round(amount / len(split_ids), 2)
        for sid in split_ids:
            db.execute(
                "INSERT INTO expense_shares (id, expense_id, sharer_id, share_amount) VALUES (?, ?, ?, ?)",
                (str(uuid.uuid4()), expense_id, sid, share),
            )

    db.commit()
    expense = dict_row(db.execute(
        "SELECT id, amount, description, payer_id, group_id, expense_type, category, timestamp, created_at FROM expenses WHERE id = ?",
        (expense_id,),
    ).fetchone())
    db.close()
    return jsonify({"message": "Expense added", "expense": expense}), 201


@bp.route("/<group_id>/expenses", methods=["GET"])
@login_required
def get_expenses(group_id):
    db = get_db()
    if not is_member(db, group_id, request.user_id):
        db.close()
        return jsonify({"error": "Access denied"}), 403

    rows = db.execute(
        """SELECT DISTINCT e.id, e.amount, e.description, e.payer_id, e.expense_type, e.category, e.timestamp, e.created_at,
                  u.name as payer_name
           FROM expenses e JOIN users u ON e.payer_id = u.id
           LEFT JOIN expense_shares es ON e.id = es.expense_id
           WHERE e.group_id = ? AND (e.payer_id = ? OR es.sharer_id = ?)
           ORDER BY e.timestamp DESC""",
        (group_id, request.user_id, request.user_id),
    ).fetchall()
    db.close()
    return jsonify({"expenses": [dict(r) for r in rows]}), 200


@bp.route("/<group_id>/expenses/<expense_id>", methods=["DELETE"])
@login_required
def delete_expense(group_id, expense_id):
    db = get_db()
    if not is_member(db, group_id, request.user_id):
        db.close()
        return jsonify({"error": "Access denied"}), 403

    expense = db.execute("SELECT id, payer_id FROM expenses WHERE id = ? AND group_id = ?", (expense_id, group_id)).fetchone()
    if not expense:
        db.close()
        return jsonify({"error": "Expense not found"}), 404

    # Only the person who logged the expense (payer) can delete it
    if expense["payer_id"] != request.user_id:
        db.close()
        return jsonify({"error": "Only the person who logged this expense can delete it"}), 403

    db.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    db.commit()
    db.close()
    return jsonify({"message": "Expense deleted"}), 200



@bp.route("/<group_id>/balances", methods=["GET"])
@login_required
def get_balances(group_id):
    db = get_db()
    if not is_member(db, group_id, request.user_id):
        db.close()
        return jsonify({"error": "Access denied"}), 403

    members = db.execute(
        "SELECT u.id, u.name FROM users u JOIN group_members fm ON u.id = fm.user_id WHERE fm.group_id = ?",
        (group_id,),
    ).fetchall()

    # Calculate net balance per person: paid - owed
    balances = {}
    names = {}
    for m in members:
        balances[m["id"]] = 0.0
        names[m["id"]] = m["name"]

    paid = db.execute(
        "SELECT payer_id, SUM(amount) as total FROM expenses WHERE group_id = ? AND expense_type = 'shared' GROUP BY payer_id",
        (group_id,),
    ).fetchall()
    for p in paid:
        if p["payer_id"] in balances:
            balances[p["payer_id"]] += float(p["total"])

    owed = db.execute(
        """SELECT es.sharer_id, SUM(es.share_amount) as total
           FROM expense_shares es JOIN expenses e ON es.expense_id = e.id
           WHERE e.group_id = ? AND e.expense_type = 'shared'
           GROUP BY es.sharer_id""",
        (group_id,),
    ).fetchall()
    for o in owed:
        if o["sharer_id"] in balances:
            balances[o["sharer_id"]] -= float(o["total"])

    # Factor in confirmed settlements
    settlements = db.execute(
        "SELECT debtor_id, creditor_id, amount FROM settlements WHERE group_id = ? AND status = 'confirmed'",
        (group_id,),
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


@bp.route("/<group_id>/activity", methods=["GET"])
@login_required
def get_activity(group_id):
    db = get_db()
    if not is_member(db, group_id, request.user_id):
        db.close()
        return jsonify({"error": "Access denied"}), 403

    # Optional filters
    from_date = request.args.get("from")
    to_date = request.args.get("to")
    member_id = request.args.get("memberId")

    # Build date filter clause
    date_clause = ""
    date_params = []
    if from_date:
        date_clause += " AND {ts} >= ?"
        date_params.append(from_date)
    if to_date:
        date_clause += " AND {ts} <= ?"
        date_params.append(to_date)

    # Fetch expenses visible to current user, with sharers
    exp_date = date_clause.replace("{ts}", "e.timestamp")
    exp_params = [group_id, request.user_id, request.user_id] + date_params
    if member_id:
        exp_member = " AND (e.payer_id = ? OR es2.sharer_id = ?)"
        exp_params += [member_id, member_id]
    else:
        exp_member = ""

    expenses = db.execute(
        """SELECT DISTINCT e.id, e.amount, e.description, e.payer_id, e.category, e.timestamp,
                  u.name as payer_name
           FROM expenses e
           JOIN users u ON e.payer_id = u.id
           LEFT JOIN expense_shares es ON e.id = es.expense_id
           LEFT JOIN expense_shares es2 ON e.id = es2.expense_id
           WHERE e.group_id = ? AND (e.payer_id = ? OR es.sharer_id = ?)"""
        + exp_date + exp_member + " ORDER BY e.timestamp DESC",
        exp_params,
    ).fetchall()

    # For each expense, get its sharers
    activity = []
    for e in expenses:
        sharers = db.execute(
            "SELECT es.sharer_id, es.share_amount, u.name FROM expense_shares es JOIN users u ON es.sharer_id = u.id WHERE es.expense_id = ?",
            (e["id"],),
        ).fetchall()
        activity.append({
            "type": "expense",
            "id": e["id"],
            "timestamp": e["timestamp"],
            "amount": float(e["amount"]),
            "description": e["description"],
            "category": e["category"],
            "payer_id": e["payer_id"],
            "payer_name": e["payer_name"],
            "sharers": [{"id": s["sharer_id"], "name": s["name"], "share": float(s["share_amount"])} for s in sharers],
        })

    # Fetch settlements
    stl_date = date_clause.replace("{ts}", "s.created_at")
    stl_params = [group_id] + date_params
    stl_member_clause = ""
    if member_id:
        stl_member_clause = " AND (s.debtor_id = ? OR s.creditor_id = ?)"
        stl_params += [member_id, member_id]

    settlements = db.execute(
        """SELECT s.id, s.amount, s.status, s.created_at, s.confirmed_at,
                  s.debtor_id, d.name as debtor_name,
                  s.creditor_id, c.name as creditor_name
           FROM settlements s
           JOIN users d ON s.debtor_id = d.id
           JOIN users c ON s.creditor_id = c.id
           WHERE s.group_id = ?""" + stl_date + stl_member_clause + " ORDER BY s.created_at DESC",
        stl_params,
    ).fetchall()

    for s in settlements:
        activity.append({
            "type": "settlement",
            "id": s["id"],
            "timestamp": s["confirmed_at"] or s["created_at"],
            "amount": float(s["amount"]),
            "status": s["status"],
            "debtor_id": s["debtor_id"],
            "debtor_name": s["debtor_name"],
            "creditor_id": s["creditor_id"],
            "creditor_name": s["creditor_name"],
        })

    # Sort everything by timestamp descending
    activity.sort(key=lambda x: x["timestamp"] or "", reverse=True)

    db.close()
    return jsonify({"activity": activity}), 200


