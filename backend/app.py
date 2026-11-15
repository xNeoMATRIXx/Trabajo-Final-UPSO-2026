"""Punto de entrada Flask. Registra blueprints y CORS."""
from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from routes.auth import auth_bp
from routes.catalog import catalog_bp
from routes.skills import skills_bp
from routes.projects import projects_bp
from routes.public import public_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, resources={r"/*": {"origins": "*"}})

    app.register_blueprint(auth_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(skills_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(public_bp)

    @app.route("/")
    def index():
        return jsonify({
            "service": "Portfolio Devs API",
            "status": "ok",
            "endpoints": [
                "POST /auth/register",
                "POST /auth/login",
                "DELETE /auth/me",
                "GET /lenguajes",
                "GET /tecnologias",
                "GET|POST|PUT|DELETE /habilidades",
                "GET|POST|PUT|DELETE /proyectos",
                "GET /u/<username>",
            ],
        })

    @app.errorhandler(400)
    def _400(error):
        return jsonify({
            "error": "solicitud_invalida",
            "mensaje": error.description
        }), 400

    @app.errorhandler(404)
    def _404(_):
        return jsonify({"error": "not_found"}), 404

    @app.errorhandler(405)
    def _405(_):
        return jsonify({"error": "method_not_allowed"}), 405

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG)