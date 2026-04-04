import os
from decimal import Decimal
from flask import Flask, jsonify, render_template
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
from datetime import datetime, date, timezone

import config
from database import init_db, get_db
import routes_auth
import routes_flats
import routes_expenses
import routes_settlements
import routes_receipt


class _SafeJSON(DefaultJSONProvider):
    """Handle Decimal and datetime from Postgres."""
    @staticmethod
    def default(o):
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        return DefaultJSONProvider.default(o)

# Resolve template dir relative to this file (works on Vercel too)
_dir = os.path.dirname(os.path.abspath(__file__))


def create_app():
    app = Flask(__name__, template_folder=os.path.join(_dir, "templates"))
    app.json_provider_class = _SafeJSON
    app.json = _SafeJSON(app)
    CORS(app)

    app.register_blueprint(routes_auth.bp)
    app.register_blueprint(routes_flats.bp)
    app.register_blueprint(routes_expenses.bp)
    app.register_blueprint(routes_settlements.bp)
    app.register_blueprint(routes_receipt.bp)

    @app.route("/")
    def index():
        return render_template("base.html")

    @app.route("/health")
    def health():
        # Test DB connection too
        db_status = "unknown"
        try:
            db = get_db()
            db.execute("SELECT 1")
            db.close()
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {e}"
        return jsonify({
            "status": "ok",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": db_status,
        })

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error", "detail": str(e)}), 500

    return app


if __name__ == "__main__":
    init_db()
    app = create_app()
    print(f"ShareSense running on http://localhost:{config.PORT}")
    app.run(host="0.0.0.0", port=config.PORT, debug=True)
