import random
import time

from flask import Flask, jsonify, request


def create_test_app():
    app = Flask(__name__)

    @app.route("/authenticated", methods=["GET"])
    def authenticated():
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Unauthorized"}), 401
        return jsonify({"message": "Authenticated successfully"}), 200

    @app.route("/read_me", methods=["GET"])
    def read_me():
        return "This is a dummy README", 200

    @app.route("/returns_list", methods=["GET"])
    def returns_list():
        return (
            jsonify(
                [
                    {"name": "ruff", "fullname": "astral-sh/ruff"},
                    {"name": "uv", "fullname": "astral-sh/uv"},
                    {"name": "ty", "fullname": "astral-sh/ty"},
                ]
            ),
            200,
        )

    @app.route("/always_fail", methods=["GET"])
    def always_fail():
        return jsonify({"success": False}), 400

    @app.route("/always_succeed", methods=["GET"])
    def always_succeed():
        return jsonify({"success": True}), 200

    @app.route("/randomly_succeed", methods=["GET"])
    def randomly_succeed():
        if random.random() < 0.75:
            return jsonify({"success": False}), 402
        else:
            return jsonify({"success": True}), 200

    @app.route("/slow_endpoint", methods=["GET"])
    def slow_endpoint():
        time.sleep(30)
        return jsonify({"success": True}), 200

    return app


def run_server(host: str, port: int):
    app = create_test_app()
    app.run(host=host, port=port, debug=False)
