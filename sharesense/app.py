from flask import Flask, jsonify, render_template
from flask_cors import CORS
from datetime import datetime, timezone

import config
from database import init_db
import routes_auth
import routes_flats
import routes_expenses
import routes_settlements


def create_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(routes_auth.bp)
    app.register_blueprint(routes_flats.bp)
    app.register_blueprint(routes_expenses.bp)
    app.register_blueprint(routes_settlements.bp)

    @app.route("/")
    def index():
        return render_template("base.html")

    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()})

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app


if __name__ == "__main__":
    init_db()
    app = create_app()
    print(f"ShareSense running on http://localhost:{config.PORT}")
    app.run(host="0.0.0.0", port=config.PORT, debug=True)
